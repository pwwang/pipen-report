"""An example of using pipen-report to generate reports"""
# also need to install pipen-filters
from pathlib import Path
from pipen import Proc, Pipen, ProcGroup


class MyProcGroup(ProcGroup):
    """A process group"""

    @ProcGroup.add_proc
    def p_pg1(self):

        class PG1(Proc):
            """Copy the image over"""
            input = "inimg:file"
            output = "outimg:file:{{in.inimg | basename}}"
            script = "cp {{in.inimg}} {{out.outimg}}"
            plugin_opts = {
                "report": """
                <script>
                    import { Image } from '$lib';
                </script>
                <h1>Image</h1>
                <Image src="{{ job.in.inimg }}" />
                """,
            }

        return PG1

    @ProcGroup.add_proc
    def p_pg2(self):

        class PG2(self.p_pg1):
            """Copy the image over 2"""
            requires = self.p_pg1

        return PG2


pg = MyProcGroup()


class ProcessNoTOC(Proc):
    """Report report_toc = False"""
    input = "inimg:file"
    requires = pg.starts
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = "cp {{in.inimg}} {{out.outimg}}"
    plugin_opts = {
        "report": """
        <script>
            import { Image, Descr } from '$lib';
        </script>
        <h1>Image</h1>
        <Descr>This is a description about the section.</Descr>
        <Image src="{{ job.in.inimg }}" />
        """,
        "report_toc": False,
    }


class ProcessWithPagingWithAVeryLongProcessName(Proc):
    """Report with paging"""
    requires = ProcessNoTOC
    input = "inimg:file"
    # Use variable to skip checking
    output = "outimg:file:{{in.inimg | basename}}"
    script = """
        cp {{in.inimg}} {{out.outimg}}
        report_file={{job.outdir}}/report.json
        table_file={{job.outdir}}/table.txt
        echo -e 'A\tB\tC\tD' > $table_file
        for i in {1..10}; do
            echo -e "$i$i$i\t$i$i$i\t$i$i$i\t$i$i$i" >> $table_file
        done
        image={{out.outimg}}
        {% raw %}
        echo "{" > $report_file
        echo '  "Section 1": {' >> $report_file
        echo '    "Image" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "descr",' >> $report_file
        echo '            "title": "Description title",' >> $report_file
        echo '            "style": "background-color: #e4e8ff",' >> $report_file
        echo '            "content": "<p>This is a description about the section.</p><p>This is a description in another paragraph.</p>"' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    },' >> $report_file
        echo '    "Table": {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "table",' >> $report_file
        echo "            \\"data\\": {\\"file\\": \\"$table_file\\"}," >> $report_file
        echo '            "src": true' >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "The following are the tables of images": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "tabs": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 1",' >> $report_file
        echo '            "ui": "table_of_images",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 1",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 2",' >> $report_file
        echo '            "ui": "table_of_images",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 2",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 3",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 3",' >> $report_file
        echo '            "ui": "table_of_images:3",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 4",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 5",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 6",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Accordion": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "accordion": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 1",' >> $report_file
        echo '            "ui": "table_of_images",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 1",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 2",' >> $report_file
        echo '            "ui": "table_of_images",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 2",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 3",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "title": "Table of Images 3",' >> $report_file
        echo '            "ui": "table_of_images:3",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 4",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 5",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              },' >> $report_file
        echo '              {' >> $report_file
        echo '                "title": "Image 6",' >> $report_file
        echo '                "descr": "This is a description about the image.",' >> $report_file
        echo "                \\"src\\": \\"$image\\"" >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Error": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "error",' >> $report_file
        echo '            "content": "This is an error message."' >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Lists": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "tabs": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "ui": "flat",' >> $report_file
        echo '            "title": "Unordered List",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "kind": "list",' >> $report_file
        echo '                "ordered": false,' >> $report_file
        echo '                "items": [' >> $report_file
        echo '                  "Item 1",' >> $report_file
        echo '                  "Item 2",' >> $report_file
        echo '                  "Item 3"' >> $report_file
        echo '                ]' >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "ui": "flat",' >> $report_file
        echo '            "title": "Ordered List",' >> $report_file
        echo '            "contents": [' >> $report_file
        echo '              {' >> $report_file
        echo '                "kind": "list",' >> $report_file
        echo '                "ordered": true,' >> $report_file
        echo '                "items": [' >> $report_file
        echo '                  "Item 1",' >> $report_file
        echo '                  "Item 2",' >> $report_file
        echo '                  "Item 3"' >> $report_file
        echo '                ]' >> $report_file
        echo '              }' >> $report_file
        echo '            ]' >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "DropDownSwitcher": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "dropdown_switcher:1": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "ds_name": "Select an item ..."' >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo '            "ds_name": "Image 1",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          },' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo '            "ds_name": "Image 2",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Table#2": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "table",' >> $report_file
        echo "            \\"src\\": \\"$table_file\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Image#2": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Table#3": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "table",' >> $report_file
        echo "            \\"src\\": \\"$table_file\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Image#3": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Table#4": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "table",' >> $report_file
        echo "            \\"src\\": \\"$table_file\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Image#4": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Table#5": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "table",' >> $report_file
        echo "            \\"src\\": \\"$table_file\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  },' >> $report_file
        echo '  "Image#5": {' >> $report_file
        echo '    "#" : {' >> $report_file
        echo '      "#" : {' >> $report_file
        echo '        "flat": [' >> $report_file
        echo '          {' >> $report_file
        echo '            "kind": "image",' >> $report_file
        echo "            \\"src\\": \\"$image\\"" >> $report_file
        echo '          }' >> $report_file
        echo '        ]' >> $report_file
        echo '      }' >> $report_file
        echo '    }' >> $report_file
        echo '  }' >> $report_file
        echo '}' >> $report_file
        {% endraw %}
    """  # noqa: E501
    plugin_opts = {
        "report": """
        <script>
            import { Image, DataTable, Descr } from '$lib';
            import { Dropdown, Tabs, TabContent, Tab, Accordion, AccordionItem, InlineNotification, UnorderedList, OrderedList, ListItem } from '$ccs';
        </script>

        {{ job | render_job }}
        """,  # noqa: E501
        "report_paging": 4,
        "report_force_build": True,
    }


class ProcessWithoutHeadings(Proc):
    """A process without headings"""
    requires = ProcessWithPagingWithAVeryLongProcessName
    input = "inimg:file"
    output = "outimg:file:{{in.inimg | basename}}"
    script = """
        cp {{in.inimg}} {{out.outimg}}
    """
    plugin_opts = {
        "report": """
            <script>
                import { Iframe } from '$lib';
            </script>
            <Iframe style="height:50vh" src="index.html" />
            <Iframe style="height:50vh" src="https://google.com" />
        """
    }


class Pipeline(Pipen):
    outdir = "./output"
    starts = pg.starts
    data = [[Path(__file__).parent.resolve().joinpath("placeholder.png")]]
    plugin_opts = {
        # "report_no_collapse_pgs": True,
        "report_loglevel": "debug",
    }


if __name__ == "__main__":
    Pipeline().run()
