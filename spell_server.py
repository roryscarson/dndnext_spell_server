from json import loads
from urllib import unquote_plus
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from StringIO import StringIO


SERVER_ADDRESS = ''
SERVER_PORT = 8080
SPELLS_DATABASE = 'DnDnext spells.json'
SPELLS_TEMPLATE = 'spell_server.html'


class DndSpellsWeb(SimpleHTTPRequestHandler):

    def __init__(self, request, client_address, server):

        # Load spell data
        try:
            with open(SPELLS_DATABASE) as json_file:
                self.json_data = loads(json_file.read())
        except:
            exit("Error loading '%s' data." % SPELLS_DATABASE)

        # Load spell template
        try:
            with open(SPELLS_TEMPLATE) as template_file:
                self.template_data = template_file.read()
        except:
            exit("Error loading template file '%s'." % SPELLS_TEMPLATE)

        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

    def send_head(self):

        body = None

        if self.path=='/':
            body = self.parse_index()
        else:
            try:
                spell_end = self.path.index('/', 1)
            except:
                return SimpleHTTPRequestHandler.send_head(self)
            if spell_end>1:
                spell_name = unquote_plus(self.path[1:spell_end])
                for spell in self.json_data:
                    if spell['title']==spell_name:
                        body = self.parse_spell(spell)
                if body is None:
                    self.send_error(404, "Spell '%s' not found." % spell_name)
                    return None

        # Send body or default handler
        if body:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return StringIO(body)
        else:
            return SimpleHTTPRequestHandler.send_head(self)

    def parse_index(self):
        response = self.template_data
        cut_from = response.index(u"<main>")
        cut_to = response.index(u"</main>")
        return response[0:cut_from-1] + response[cut_to+8:]

    def parse_spell(self, spell):
        spell_title = u''
        spell_subtitle = u''
        spell_properties = []
        spell_p = []
        for field in spell:
            if field=="title":
                spell_title = spell[field]
            elif field=="contents":
                for content in spell[field]:

                    try:
                        if content.index("subtitle")==0:
                            spell_subtitle = content[11:]
                    except:
                        pass

                    try:
                        if content.index("property")==0:
                            spell_properties.append(content[11:])
                    except:
                        pass

                    try:
                        if content.index("fill")==0:
                            brs = int(content[7:])
                            for br in brs:
                                spell_p.append("")
                    except:
                        pass

                    try:
                        if content.index("text")==0:
                            spell_p.append(content[7:])
                    except:
                        pass

        spell_content = u''

        if spell_title:
            spell_content += u"<header><h1>" + spell_title + u"</h1>"
            if spell_subtitle:
                spell_content += u"<p>" + spell_subtitle + u"</p>"
            spell_content += u"</header>"

        if spell_properties:
            spell_content += u"<ul>"
            for prop in spell_properties:
                spell_content += u"<li>" + prop + u"</li>"
            spell_content += u"</ul>"

        if spell_p:
            for p in spell_p:
                spell_content += u"<p>" + (u"&nbsp;" if p==u"" else p) + u"</p>"

        response = self.template_data
        cut_from = response.index(u"<main>")
        cut_to = response.index(u"</main>")
        return response[0:cut_from+6] + spell_content + response[cut_to:]


# Server
server_address = (SERVER_ADDRESS, SERVER_PORT)
httpd = TCPServer(server_address, DndSpellsWeb)
server_name = 'localhost' if server_address[0] == '' else server_address[0]
print "http://%s:%s" % (server_name, server_address[1])
httpd.serve_forever()
