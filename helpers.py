import urllib.parse
from datetime import datetime
from pyracing.constants import Category


iracing_table_css = """#iracing_table {
                  font-family: Arial, Helvetica, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }

                #iracing_table td, #iracing_table th {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                #iracing_table tr:nth-child(even){background-color: #f2f2f2;}

                #iracing_table th {
                  padding-top: 10px;
                  padding-bottom: 10px;
                  text-align: left;
                  background-color: #4CAF50;
                  color: white;
                }
                
                """

leaderboard_table_css = """#iracing_table {
                  font-family: Arial, Helvetica, sans-serif;
                  border-collapse: collapse;
                  width: 100%;
                }

                #iracing_table td, #iracing_table th {
                  border: 1px solid #ddd;
                  padding: 8px;
                }

                #iracing_table tr:nth-child(even){background-color: #f2f2f2;}

                #iracing_table th {
                  padding-top: 10px;
                  padding-bottom: 10px;
                  text-align: left;
                  background-color: #f40000;
                  color: white;
                }

                """

header_css = """
    #header {
      font-family: Arial, Helvetica, sans-serif;
    }
    
"""


def build_html_header_string(header_string):
    return f"<h2 id=\"header\" style=\"text-align:center\">{header_string}</h2>"


def wrap_in_style_tag(string):
    return '<style>' + string + '</style>'


def add_backticks(string):
    return '```' + string + '```'


def lowercase_to_readable_categories(category):
    if category == 'road':
        return 'Road'
    elif category == 'oval':
        return 'Oval'
    elif category == 'dirtroad':
        return 'Dirt Road'
    elif category == 'dirtoval':
        return 'Dirt Oval'


def category_id_from_string(string):
    if string == 'road':
        return Category.road.value
    if string == 'oval':
        return Category.oval.value
    if string == 'dirtroad':
        return Category.dirt_road.value
    if string == 'dirtoval':
        return Category.dirt_oval.value


def parse_encoded_string(string):
    return urllib.parse.unquote(string).replace('+', ' ')


def get_current_year_stats(yearly_stats_list):
    """This takes the massive list of a user's yearly stats dicts
    and returns just the yearly stats from the current year"""
    current_year = str(datetime.now().year)
    return filter(lambda x: x['year'] == current_year, yearly_stats_list)
