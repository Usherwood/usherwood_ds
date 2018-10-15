#!/usr/bin/env python

"""Functions for plotting taxonomy categories"""

__author__ = "Peter J Usherwood"
__python_version__ = "3.6"


def create_map(attribute_cols):

    max_depth = check_max_depth(attribute_cols)

    level_tags = split_tags_to_levels(attribute_cols=attribute_cols,
                                      max_depth=max_depth)
    level_tags, summary_tags = create_summary_tags(level_tags=level_tags,
                                                   max_depth=max_depth)
    level_maps = create_level_maps(level_tags=level_tags,
                                   summary_tags=summary_tags,
                                   max_depth=max_depth)
    return level_maps


def check_max_depth(attribute_cols):
    max_depth = 0
    tag_depths = [(len(tag.split('.')) - 1) for tag in attribute_cols]
    max_depth = max(tag_depths)

    return max_depth


def split_tags_to_levels(attribute_cols, max_depth):
    """
    Split the list of tags in attribute cols into sub lists grouped by level

    :param attribute_cols: List[str], complete list of categories
    :param max_depth:  Int, Max depth of categories

    :return: list of lists where each sub list are the tags of that level, starting with the lowest
    """

    level_tags = []
    for i in range(0, max_depth):
        level = max_depth - i
        current_level_tags = []
        for att in attribute_cols:
            att_level = len(att.split('.')) - 1
            if att_level == level:
                current_level_tags += [att]

        level_tags.append(current_level_tags)

    return level_tags


def create_summary_tags(max_depth, level_tags):
    summary_tags = []
    for i in range(0, max_depth):
        level = max_depth - i
        current_summary_tags = []
        for att in level_tags[i]:
            summary_tag = ".".join(att.split('.')[:-1]) + '-ALL'
            current_summary_tags += [summary_tag]

        current_summary_tags = list(set(current_summary_tags))
        summary_tags.append(current_summary_tags)

        if i <= max_depth - 2:
            level_tags[i + 1] += current_summary_tags

    return level_tags, summary_tags


def create_level_maps(max_depth, level_tags, summary_tags):
    """
    stage three, create map of summary = column of same name in level above + all tags containing in level

    :param max_depth:
    :param level_tags:
    :param summary_tags:

    :return:
    """

    level_maps = []
    for i in range(0, max_depth - 1):
        level_map = dict()
        level = max_depth - i
        for summary in summary_tags[i]:
            all_sub_tags = [att for att in level_tags[i] if summary[:-4] == ".".join(att.split('.')[:-1])]
            matching_tag_above = [att for att in level_tags[i + 1] if summary[:-4] == att]
            level_map[summary] = all_sub_tags + matching_tag_above

        level_maps.append(level_map)

    return level_maps


def populate_df_with_macro_cats(df, level_maps):
    """
    Populates the columns in a df populated with sub categories

    :param df: df with the sub tags already populated
    :param level_maps: level_maps as created above

    :return: df with summary columns
    """
    for level_map in level_maps:
        for summary_att, atts in level_map.items():
            df[summary_att] = df[atts].sum(axis=1).apply(lambda e: 1 if e >= 1 else 0)

    return df
