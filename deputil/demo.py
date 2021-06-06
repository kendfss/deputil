"""
Scrape a python package for its external dependencies
todo
    venv support
    use paths to further identify inexplicitly relative imports
"""
__all__ = "scan_sourcefile scan_package standard_modules version".split()

from warnings import warn
from typing import Iterable, Iterator, Any, Callable
from string import punctuation
import os, re, sys

common_encodings = "utf-8 iso-8859-5".split()

def error_position(error:str) -> int:
    match = re.search("(?P<space1>\s)(?P<number>\d+):(?P<space2>\s)", str(error))
    return int(match.groupdict()['number'])

def line_from_position(message:Exception, path:str, encoding:str='utf-8') -> int:
    position = error_position(message)
    with open(path, 'r', encoding=encoding) as fob:
        ctr = 0
        for i, line in enumerate(fob.readlines(), 1):
            try:
                for char in line:
                    ctr += 1
                    if ctr == position: 
                        return i
            except UnicodeDecodeError:
                return i

def unique(iterable:Iterable[Any], yielded:list=None) -> Iterator[Any]:
    """
    Iterate over unique elements of an iterable
    examples:
        >>> [*unique('abbcccdddd')]
        ['a', 'b', 'c', 'd']
        >>> [*unique('abcd')]
        ['a', 'b', 'c', 'd']
    """
    yielded = yielded if not isinstance(yielded, type(None)) else []
    for i in iterable:
        if not i in yielded:
            yield i
            yielded.append(i)

def parse_extensions(extensions) -> re.Pattern:
    """
    Create a regex parser to check for file extensions. 
        Note: Separate extensions by any one of
            [',', '`', '*', ' ']
    """
    exts = extensions.replace('.', '')
    sep = [i for i in ',`* ' if i in exts]
    pattern = '|'.join(f'\.{i}$' for i in exts.split(sep[0] if sep else None))
    pat = re.compile(pattern, re.I)
    return pat

def files(root:str='.', exts:str='') -> Iterator[str]:
    """
    Search for files along a directory's tree.
    Also (in/ex)-clude any whose extension satisfies the requirement
        
    Params
        root: str|pathlike|Place
            path to starting directory
        exts
            extensions of interest. 
            you can pass more than one extension at a time by separating them with any of the following:
                [',', '`', '*', ' ']
        negative
            (True -> omit, False -> include) matching extensions
        absolute
            yield (True -> abspaths, False -> names only)
    """
    root = os.path.realpath(str(root))
    pat = parse_extensions(exts)
    predicate = lambda x: bool(pat.search(x))
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            yield from files(path, exts=exts)
        elif predicate(path):
            yield path

def standard_modules() -> Iterator[str]:
    """
    Every module found:
        under your installation's /lib directory; excuding any under /lib/site-packages/*
        sys.builtin_module_names
    """
    omitables = 'site-packages __pycache__ .pyo .ico .dll .pdb'.split()
    
    path = lambda folder: os.path.join(sys.exec_prefix, folder)
    tidy = lambda pth: os.path.split(os.path.splitext(pth)[0])[-1]
    discriminant = lambda pth: not any(re.search(i, pth) for i in map(re.escape, omitables))
    
    lib = map(tidy, filter(discriminant, os.listdir(path('lib'))))
    dlls = map(tidy, filter(discriminant, os.listdir(path('DLLs'))))
    
    yielded = ['__main__']
    yield from yielded
    yield from unique(sys.builtin_module_names, yielded)
    yield from unique(lib, yielded)
    yield from unique(dlls, yielded)
    
def name_parser(statement:str) -> Iterator[str]:
    """
    Parse the name of the imported module from the line its on
    """
    if 'from' in statement:
        name = statement.split()[1]
        # if name != '.':
        if not name in punctuation:
            yield statement.split()[1]
    else:
        onames = statement.split()[1:]
        nnames = []
        for i, name in enumerate(onames):
            if name=='as' or onames[i-1]=='as' or name in punctuation:
                continue
            nnames.append(name.replace(',', '').strip())
        yield from filter(lambda x: not (x.startswith('.') or x=='.'), nnames)

def scan_sourcefile(path, keywords='import from'.split(), encoding='utf-8', versions:bool=False):
    standards = set(standard_modules())
    with open(path, 'r', encoding=encoding) as fob:
        kwrd = '|'.join([f'^{kw}' for kw in map(re.escape, keywords)])
        try:
            for line in fob.readlines():
                if re.search(kwrd, line):
                    names = name_parser(line)
                    for name in names:
                        if all(not p in name for p in punctuation):
                            if not name in standards:
                                # yield name
                                yield f"{name} >= {v}" if versions and (v:=version(name)) else name
                            
        except UnicodeDecodeError as e:
            warn(f"UnicodeDecodeError[char={error_position(e)}] in {path}\n", Warning)
            return []

def version(module_name:str, raise_noattr:bool=False, raise_unfound:bool=False) -> str|type(None):
    try:
        exec(f'import {module_name}')
        return eval(f'{module_name}.__version__')
    except AttributeError:
        if raise_noattr:
            raise
    except ModuleNotFoundError:
        if raise_unfound:
            raise

def scan_package(root:str, versions:bool=True, exts:str='py', scanner:Callable=scan_sourcefile, natives:set[str]=set(standard_modules())) -> Iterator[str]:
    """
    Scan a package and return its input path
    """
    expat = parse_extensions(exts)
    for path in files(root):
        if expat.search(path):
            for name in scanner(path, versions=versions):
                if not name.split()[0] in natives:
                    yield name
                    natives.add(name.split()[0])


def show(items:Iterable[Any], indentation:int=0) -> list[Any]:
    out = []
    tab = '\t' * indentation
    for item in items:
        print(f"{tab}{item}")
        out.append(item)
    return out
if __name__ == '__main__':
    paths = r"""E:\languages\Python310-64\Lib\site-packages\attrs-19.3.0.dist-info
E:\languages\Python310-64\Lib\site-packages\bidict
E:\languages\Python310-64\Lib\site-packages\bidict-0.21.2.dist-info
E:\languages\Python310-64\Lib\site-packages\bitstruct
E:\languages\Python310-64\Lib\site-packages\more_itertools
E:\languages\Python310-64\Lib\site-packages\pendulum
E:\languages\Python310-64\Lib\site-packages\pendulum-2.1.2.dist-info
E:\languages\Python310-64\Lib\site-packages\tbm_utils
E:\languages\Python310-64\Lib\site-packages\tbm_utils-2.6.0.dist-info
E:\languages\Python310-64\Lib\site-packages\attr
E:\languages\Python310-64\Lib\site-packages\pprintpp-0.4.0.dist-info
E:\languages\Python310-64\Lib\site-packages\wrapt
E:\languages\Python310-64\Lib\site-packages\pprintpp
E:\languages\Python310-64\Lib\site-packages\IPython
e:/projects/monties/2021/packaging/filey/filey
E:\Projects\Monties\2021\packaging\deputil\deputil"""
    # paths = "e:/projects/monties/2021/packaging/filey/filey"
    roots = map(str.strip, paths.splitlines())
    for root in roots:
        print(root)
        show(scan_package(root, versions=True))
        print('\n')
        show(scan_package(root, versions=False))
        print('\n')