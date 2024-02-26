import os
import gradio as gr
import pandas as pd
import sys
print(sys.path)
from ticket_engine.ticket_issue import Issue

from aleph_alpha_client import (
    Client
)

class TicketEngine:
    """This class builds a ticket engine

    A ticket engine is an object which can recommend an
    action for a given IT ticket issue based on data of
    successfully solved tickets.
    It is shipped with gradio frontends,
    but it can be extended to other APIs
    """

    def __init__(
            self,
            training_folder: str,
            test_data_path: str,
            AA_TOKEN: str
    ):
        """Initialization of the issue object


             Args:
                 training_folder: Path to folder where the training data is stored
                 test_data_path: Path to a file with test issues which are used as examples
             Returns:
                 ticket Engine: An initialized ticket engine, which is able to recommend actions
        """
        self.training_folder = training_folder
        self.test_data_path = test_data_path
        self.client = Client(token=AA_TOKEN)

        # initialize training data
        self.training_df = self.load_training_issues(training_folder)
        self.training_issues = self.preprocess_training_issues(self.training_df).apply(lambda row: Issue(self.client, *row),
                                                                                       axis=1).tolist()
        self.test_df = pd.read_csv(test_data_path)
        self.test_df = self.test_df[["Issue", "Category", "Description"]]


    def preprocess_training_issues(self, df):
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

    def load_training_issues(self, folder_path):
        """ Loads issues for training the model

        This function reads in all xlsx, csv, and json files in the given folder, and creates a dataframe,
        where the data from all files is concatenated.

        Args:
            folder_path: An absolute path to the files with the data for known issues
        Returns:
            pandas.dataframe: A dataframe with all the data present in the input folder concatenated

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

    def recommend(self, test_issue: "Issue" = None, output="value"):
        """ Computes recommendations for a test_case

        This function reads in all xlsx, csv, and json files in the given folder, and creates a dataframe,
        where the data from all files is concatenated.

        Args:
            test_case: List of 3 entries (Issue theme, category, description
            output: Three options are to choose from
                - "value": returns a proposed action with score
                - "solution": returns the recommended action as string
                - "df: retruns a df with solutions and scores
        Returns:
            string / df: depending on output variable
        """
        assert bool(test_issue), "Must provide issue in form of a list."
        output_modes = ["value", "df", "solution"]
        assert output in output_modes, f"{output} is not in the list of allowed values: {output_modes}"

        results = [
            {
                "solution": known_issue.solution,
                "score": known_issue.score_issue(test_issue),
            }
            for known_issue in self.training_issues
        ]
        sorted_results = sorted(results, key=lambda d: d["score"], reverse=True)

        if output == "solution":
            return sorted_results[0]["solution"]
        elif output == "value":
            return sorted_results[0]["solution"] + " ({:.0%})".format(sorted_results[0]["score"])
        elif output == "df":
             return sorted_results


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
                  "text"]
        outputs = [gr.Textbox(label="You can try the following:")]
        # the inference function
        def infer_single(issue, category, description):
            return self.recommend(Issue(self.client, issue, category, description))

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
                               headers=["Issue", "Category", "Description"])]
        outputs = [gr.Dataframe(row_count=(1, "dynamic"), col_count=(1, "fixed"), label="Predictions",
                                headers=["recommendation for solution with percentage likelihood"])]
        # we will give our dataframe as example
        examples = self.test_df
        # the inference function
        def infer_df(input_dataframe):
            return input_dataframe.apply(lambda row: self.recommend(test_issue=Issue(self.client, *row)), axis=1).to_frame(
                name="recommendation for solution with percentage likelihood")

        gr.Interface(fn=infer_df, inputs=inputs, outputs=outputs, examples=[[examples]]).launch(share=True)