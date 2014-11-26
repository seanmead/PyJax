"""
Created on Oct 1, 2014

@author: Sean Mead

Everything in WebData is a shortcut for printing html or javascript.
"""


class Html(type):
    pass


class Script(type):
    InnerMenu = """
        <script>
            window.onload = function(){
                try{
                    loadInnerLinks();
                }catch(error){}
            };
        </script>
    """

    OuterMenu = """
        <script>
            try{
               loadOuterLinks();
            }catch(error){}
        </script>
    """

    @staticmethod
    def load(item):
        return """<script>
            try{
               load('%s');
            }catch(error){
                 window.onload = function(){load('%s')};
            }
                </script>""" % (item, item)