# python setup.py install --install-base=c:\wk\k --install-platbase=c:\wk\k --install-purelib=c:\wk\k --install-data=c:\wk\k
import os, sys
from distutils.core import setup
from Pyrex.Distutils import build_ext, Extension
#from distutils.extension import Extension
#from Cython.Distutils import build_ext


def _walkpkg(path, name, pkgs):
    for fname in os.listdir(path):
        child = os.path.join(path, fname)
        if os.path.exists(os.path.join(child, '__init__.py')):
            childname = name+"."+fname
            pkgs.append(childname)
            _walkpkg(child, childname, pkgs)

def listpkgs(path):
    name = os.path.split(path)[1]
    pkgs = [name]
    _walkpkg(path, name, pkgs)
    return pkgs

def listpyx(path):
    ret = [os.path.join(path, fname) for fname in os.listdir(path) if fname.endswith('.pyx')]
    return ret

def getext(path):
    pyrexsrc = [os.path.join(path, fname) for fname in os.listdir(path) if os.path.splitext(fname)[1] in ('.pyx', 'pxi', 'pyd')]
    cppsrc = [os.path.join(path, fname) for fname in os.listdir(path) if os.path.splitext(fname)[1] in ('.cpp', '.rc')]
    return pyrexsrc+cppsrc


def gentlb():
    os.system('midl /D "NDEBUG"  /nologo /char signed /env win32  /tlb "pymfclib.tlb" pymfclib\\pymfclib.idl')
                                
gentlb()

macros = [("WIN32", None), ("_WINDOWS", None), ("_USRDLL", None), ("_WINDLL", None),
          ("_AFXDLL", None), ("_UNICODE", None), ("UNICODE", None), 
          ("WINVER", "0x0500"), ("_WIN32_WINNT", "0x0500"), ("_WIN32_IE", "0x0501"),
          ("PYMFCDLL", None)]

extra_compile_args = ["/O2", "/FD", "/EHsc", "/MD", "/GR", "/c", "/Zi", "/TP"]
extra_link_args = ["/DEBUG", '/PDB:"pymfclib.pdb"', '/MAP:"_pymfclib.map"']


setup(name='pymfc',
      version='0.0.53',
      packages=listpkgs("pymfc"),
      ext_modules=[
          Extension('_pymfclib',
              getext("pymfclib"),
              define_macros=macros,
              extra_compile_args=extra_compile_args,
              libraries=('winmm', 'Imm32', 'htmlhelp', 'Winhttp'),
              extra_link_args=extra_link_args,
              )],
      cmdclass = {'build_ext': build_ext},
      
)

#.lib .lib
