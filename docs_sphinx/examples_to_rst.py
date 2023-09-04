from os import getcwd, listdir, path


class Parser:
    def __init__(self, file, docs_path):
        self.file = file
        self.lines = self.read_file()
        self.info_lines = self.get_info_lines()
        self.docs_path = docs_path
        self.figs_path = path.join(docs_path, 'source/examples/_static')

    def read_file(self):
        with open(self.file, 'r') as f:
            return f.read().splitlines()
    
    def get_info_lines(self):
        return [i for i, x in enumerate(self.lines) if x == '"""']
    
    def run_code(self):
        figname = self.filename.replace('.py', '.png')
        fig_path = path.join(self.figs_path, figname)
        exec(self.code.replace('show()', f'savefig("{fig_path}", dpi=300)'))

    def write_rst(self):
        filename = path.join(self.docs_path, 'source', 'examples',
                             self.filename.replace('.py', '.rst'))
        with open(filename, 'w') as f:
            f.write(self.rst_file)

    @property
    def filename(self):
        return path.basename(self.file)
    
    @property
    def title(self):
        for index, value in enumerate(self.lines):
            if value == 'Title':
                return self.lines[index + 2]
    @property
    def description(self):
        start = [i for i, x in enumerate(self.lines) if x == 'Description'][0]
        end = self.info_lines[-1]
        return '\n'.join(self.lines[start + 2:end])
    
    @property
    def code(self):
        start = self.info_lines[-1] + 1
        return '\n'.join(self.lines[start:])
    
    @property
    def rst_code(self):
        directive = '.. code-block:: python'
        indented_code = self.code.replace('\n', '\n    ')
        return '\n'.join([directive, indented_code])
    
    @property
    def rst_file(self):
        image_name = path.join('_static', self.filename.replace('.py', '.png'))
        image = (f'.. image:: {image_name}\n'
                  '   :align: center')
        content = [f"{self.title}\n{'=' * len(self.title)}",
                   self.description,
                   self.rst_code, image]
        return '\n\n\n'.join(content)
    


# Get the path to the directory that is one level up
root = path.abspath(path.join(path.dirname(__file__), '..'))
docs = path.join(root, 'docs_sphinx')
examples = path.join(root, 'examples_new')
files = listdir(examples)
filename = path.join(examples, files[0])

test = Parser(filename, docs)
# print(test.title)
# print(test.filename)
test.run_code()
test.write_rst()

