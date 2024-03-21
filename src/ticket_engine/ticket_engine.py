import os
import gradio as gr
from flask import (Flask, g, request)
import pandas as pd
from ticket_engine.ticket_issue import Issue
import pdb

from aleph_alpha_client import (
    Client, Prompt, CompletionRequest
)

class TicketEngine:
    """This class builds a ticket engine

    A ticket engine is an object which can recommend an
    action for a given IT ticket issue based on data of
    successfully solved tickets.
    It is shipped with gradio frontends,
    but it can be extended to other APIs

    Attributes:
        training_folder: Path to folder where the training data is stored
        test_data_path: Path to a file with test issues which are used as examples
    """

    def __init__(
            self,
            training_folder: str,
            test_data_path: str,
            AA_TOKEN: str
    ):

        self.training_folder = training_folder
        self.test_data_path = test_data_path
        self.client = Client(token=AA_TOKEN)

        # initialize training data
        self.training_df = self.preprocess_training_issues(self.load_training_issues(training_folder))
        self.training_issues = self.training_df.apply(lambda row: Issue(self.client, *row),axis=1).tolist()
        self.training_prompt = self.create_training_prompt()

        self.test_df = pd.read_csv(test_data_path)
        self.test_df = self.test_df[["Issue", "Category", "Description"]]


    def preprocess_training_issues(self, df : pd.DataFrame):
        """ Preprocessing function for the training issues

        This function preprocesses the training data:
         - filtering on issues which have been solved
         - enforcing schema: keeping only relevant columns

        Args:
            dataframe: A pandas data frame with the raw issues
        Returns:
            dataframe: A dataframe with all preprocessing applies

        """

        df = df[df['Resolved'] == True].drop(labels=["Resolved"], axis=1)

        return df[["Issue", "Category", "Description", "Resolution"]]

    def load_training_issues(self, folder_path: str):
        """ Loads issues for training the model

        This function reads in all xlsx, csv, and json files in the given folder, and creates a dataframe,
        where the data from all files is concatenated.

        Args:
            folder_path: An absolute path to the files with the data for known issues

        Returns:
            combined_df: A dataframe with all the data present in the input folder concatenated

        """

        excel_files = []
        csv_files = []
        json_files = []

        # List all files in the folder
        files = os.listdir(folder_path)

        # n Separate files by extension
        for file in files:
            if file.endswith(".xlsx"):
                excel_files.append(file)
            elif file.endswith(".csv"):
                csv_files.append(file)
            elif file.endswith(".json"):
                json_files.append(file)

        # Read Excel files
        excel_data = pd.concat([pd.read_excel(os.path.join(folder_path, file)) for file in excel_files],
                               ignore_index=True)

        # Read CSV files
        csv_data = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in csv_files], ignore_index=True)

        # Read JSON files
        json_data = pd.concat([pd.read_json(os.path.join(folder_path, file)) for file in json_files], ignore_index=True)

        # Concatenate all data into a single DataFrame
        combined_df = pd.concat([excel_data, csv_data, json_data], ignore_index=True)

        return combined_df

    def create_training_prompt(self, ):
        """ Computes the promt for few shot completion from the training data

        This function assembles from the training data a prompt which is used for few shot completion.

        Args:
            dataframe: A pandas data frame with the raw issues
        Returns:
            string: the few shot completion prompt as string

        """
        training_df = self.training_df
        training_df["Issue"] = "Issue: " + training_df.loc[:, 'Issue']
        training_df["Resolution"] = "\nResolution: " + training_df.loc[:, "Resolution"] + "."
        prompt_text = "Recommend a resolution for an issue.\n" + \
                        self.training_df.to_csv(header=None, index=False, lineterminator="\n###\n").replace('"', '').replace(
                          ',\n', '\n')
        return prompt_text

    def recommend_complete(self, test_data: list):
        """ Computes recommendations for a test_issue

        Computes a resolution based on few shot completion

        Args:
            test_issue: List of 3 entries (Issue theme, category, description

        Returns:
            string: resolution as completion

        """
        assert len(test_data) == 3
        prompt_text = self.training_prompt +\
                      test_data[0] + "," + test_data[1] + "," + test_data[2] +\
                      "\nResolution:"

        params = {
            "prompt": Prompt.from_text(prompt_text),
            "maximum_tokens": 16,
            "stop_sequences": [".", ",", "?", "!", "###"],
        }


        request = CompletionRequest(**params)
        response = self.client.complete(request=request, model="luminous-extended")
        completion = response.completions[0].completion

        return completion

    def recommend(self, test_data: list = None, output="value"):
        """ Computes recommendations for a test_issue

        Computes a resolution based on the cosine similarity

        Args:
            test_issue: List of 3 entries (Issue theme, category, description
            output: Three options are to choose from
                - "value": returns a proposed action with score
                - "solution": returns the recommended action as string
                - "df: retruns a df with solutions and scores
        Returns:
            string / df: depending on output variable

        """
        assert len(test_data) == 3, "Must provide issue."
        output_modes = ["value", "df", "solution", "complete"]
        assert output in output_modes, f"{output} is not in the list of allowed values: {output_modes}"

        if output == "complete":
            # use few shot completion to generate a resolution
            prompt_text = self.training_prompt + \
                          test_data[0] + "," + test_data[1] + "," + test_data[2] + \
                          "\nResolution:"

            params = {
                "prompt": Prompt.from_text(prompt_text),
                "maximum_tokens": 16,
                "stop_sequences": [".", ",", "?", "!", "###"],
            }

            request = CompletionRequest(**params)
            response = self.client.complete(request=request, model="luminous-extended")
            results = response.completions[0].completion
        else:
            # compute similarity to known issues for resolution
            test_issue = Issue(self.client, *test_data)
            similarity = [
                {
                    "solution": known_issue.solution,
                    "score": known_issue.score_issue(test_issue),
                }
                for known_issue in self.training_issues
            ]
            results = sorted(similarity, key=lambda d: d["score"], reverse=True)

        if output == "solution":
            return results[0]["solution"]
        elif output == "value":
            return results[0]["solution"] + " ({:.0%})".format(results[0]["score"])
        elif output == "df" or output == "complete":
            return results

    def gradio_single(self):
        """ Creates an interactive gradio UI to create recommendations

        This function creates a gradio UI where one can
        fill in the information needed for an IT issue
        and it prints out a recommended action

        Returns:
            gradio frontend

        """
        # compute choices for category, so that one can only choose between existing categories
        choices = list(self.training_df['Category'].unique())
        # define gradio components
        inputs = ["text", gr.Dropdown(choices, label="Category", info="Please choose one of the following categories"),
                  "text",
                  gr.Checkbox(label="Be creative?")]
        outputs = [gr.Textbox(label="You can try the following:")]

        # the inference function
        def infer_single(issue, category, description, completion_flag):
            if completion_flag:
                output_mode = "complete"
            else:
                output_mode = "value"

            result = self.recommend([issue, category, description], output_mode)
            return result

        demo = gr.Interface(
            fn=infer_single,
            inputs=inputs,
            outputs=outputs,
        )

        demo.launch(share =True)


    def gradio_df(self):
        """ Creates an interactive gradio UI to create recommendations for multiple issues

         This function creates a gradio UI where one can
         fill in a table with IT issues and it prints
         out a table with recommended actions for each issue

         Returns:
             gradio frontend

         """
        # define gradio components
        inputs = [gr.Dataframe(row_count=(1, "dynamic"), col_count=(3, "fixed"), label="Input Data", interactive=1,
                               headers=["Issue", "Category", "Description"]),
                  gr.Checkbox(label="Be creative?")]
        outputs = [gr.Dataframe(row_count=(1, "dynamic"), col_count=(1, "fixed"), label="Predictions",
                                headers=["recommendation for resolution"])]
        # we will give our dataframe as example
        examples = self.test_df
        # the inference function
        def infer_df(input_dataframe, completion_flag):
            if completion_flag:
                output_mode = "complete"
            else:
                output_mode = "value"

            result = input_dataframe.apply(lambda row: self.recommend(test_data=row, output=output_mode),
                                         axis=1).to_frame(name="recommendation for resolution")
            return result

        gr.Interface(fn=infer_df, inputs=inputs, outputs=outputs, examples=[[examples]]).launch(share=True)

    def flask_endpoint(self):
        """ Creates a flask http REST endpoint to create recommendations

        This function starts a flask server where one can
        get recommendations through a REST API

        Returns:
            flask server

        """
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY='dev',
            ENGINE= self
        )

        # API endpoint
        @app.route('/recommend', methods=['POST'])
        def recommend():
            issue = request.form['issue']
            category = request.form['category']
            description = request.form['description']
            mode = request.form['mode']
            error = None

            if mode not in ("value", "complete"):
                error = 'Mode not supported'

            if not issue:
                error = 'Issue is required.'

            if not category:
                error = 'Category is required.'

            if not description:
                error = 'Description is required.'

            if error is not None:
                flash(error)

            else:
                with app.app_context():
                    return app.config['ENGINE'].recommend([issue, category, description], mode)
            return abort(400, 'Invalid input data')

        app.run()