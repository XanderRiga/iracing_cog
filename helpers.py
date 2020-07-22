iracing_table_css = """#iracing_table {
                  font-family: "Comic Sans MS", Arial, Helvetica, sans-serif;
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

header_css = """
    #header {
      font-family: "Comic Sans MS", Arial, Helvetica, sans-serif;
    }
    
"""


def build_html_header_string(header_string):
    return f"<h2 id=\"header\" style=\"text-align:center\">{header_string}</h2>"


def wrap_in_style_tag(string):
    return '<style>' + string + '</style>'
