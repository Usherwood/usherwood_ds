#!/usr/bin/env python

"""Capability for mass tagging of text snippets using regex query writing."""

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"
__spark_version__ = "2.1.1"

import pyspark
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

import regex
import csv

from utils.linguistics.text_mining.feature_extraction.categorizer.translate_rules import translate_batch

sc = pyspark.SparkContext.getOrCreate()
sql = pyspark.SQLContext(sc)

class Categorizer():
    """
    The parent class for creating and viewing labeled categories on a dataframe of snippets and other metadata
    """

    def __init__(self, df_path, sc=sc, sql=sql, id_field='Url', snippet_field='Cleaned Snippet'):
        """
        :param df_path: Pandas df containing cleaned snippets and ids (as a maximum)
        :param sc: spark context
        :param sql: spark.sql context
        :param id_field: the id field in source df
        :param snippet_field: the field containing the text data to search in
        """

        self.df_path = df_path
        self.sc = sc
        self.sql = sql
        self.df = (sql.read
                   .format("com.databricks.spark.csv")
                   .option("header", "true")
                   .load(self.df_path))
        self.rulelist_filename = None
        self.rulelist = None
        self.id_field = id_field
        self.snippet_field = snippet_field


    def load_rule_list(self, rulelist_filename, accents=False):
        """
        Step - repeatable, loads in a csv rulelist from the hdd. This rulelist should have a header row and be
        formatted into two columns, each row corresponds to one catagory:
        The first should contain the catagory names
        The second should contain the boolean search queries

        This should be created and saved in utf-8, note this CANNOT BE DONE IN EXCEL, use google docs or text editor

        :param rulelist_filename: Filename (and relative path) to the rulelist file.
        """
        print(rulelist_filename)

        self.rulelist_filename = rulelist_filename
        self.rulelist = []

        outputf = rulelist_filename.replace('.csv','Translated_Regex.csv')
        translate_batch(rulelist_filename,outputf, accents)
        # update rulelist filename
        self.rulelist_filename = outputf
        rulelist_filename = self.rulelist_filename

        with open(rulelist_filename, 'r', encoding='utf-8') as ofile:
            reader = ofile.readlines()
            for row in reader:
                if len(row) > 0 and row[0] != '#' and not regex.fullmatch('\s+', row):
                    x = row.split(',', 1)
                    # removing the new line character that is read in at the very end of each rule
                    x[-1] = x[-1].replace('\n', '')
                    self.rulelist += [x]

        print(self.rulelist_filename + ' has been loaded successfully')

        return True

    def categorize_rulefile(self, print_results_found=True):
        """
        Step - repeatable per rulelist, tags entries in df that match the query criteria for the loaded rulelist
        rules, one catagory per rule. Entries that match are allocated a 1, non-matched entries are given a 0. The
        output can be seen in df

        :param print_results_found: Bool, prints the number of matches
        """

        firstline = True
        for row in self.rulelist:

            if firstline:
                firstline = False
                continue

            querytitle = row[0]
            querystring = row[1]

            self.categorize_rule(querytitle=querytitle,
                                 querystring=querystring,
                                 print_results_found=print_results_found)

        print('Saving df')
        self.df.toPandas().to_csv(self.df_path, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

        return True

    def categorize_rule(self, querystring, querytitle, print_results_found):
        """
        Categorize a rule by appending a column to df with the querytitle and assigning each snippet a 0 or 1
        showing whether the rule was successful for that record, invalid rules receive a 2

        :param querystring: query to run
        :param querytitle: The category name
        :param print_results_found: Bool, print the number of each category found
        """

        print(querytitle)

        try:
            my_udf = udf(lambda s: 1 if regex.search(querystring, s, flags=regex.IGNORECASE) is not None else 0,
                         IntegerType())

            self.df = self.df.withColumn(querytitle, my_udf('Snippet'))
            if print_results_found:
                print(str(self.df.select(querytitle).rdd.flatMap(list).sum()), 'records found')
            return True
        except Exception as e:
            print(e)


