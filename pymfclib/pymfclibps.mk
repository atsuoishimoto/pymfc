
pymfclibps.dll: dlldata.obj pymfclib_p.obj pymfclib_i.obj
	link /dll /out:pymfclibps.dll /def:pymfclibps.def /entry:DllMain dlldata.obj pymfclib_p.obj pymfclib_i.obj \
		kernel32.lib rpcns4.lib rpcrt4.lib oleaut32.lib uuid.lib \
.c.obj:
	cl /c /Ox /DWIN32 /D_WIN32_WINNT=0x0400 /DREGISTER_PROXY_DLL \
		$<

clean:
	@del pymfclibps.dll
	@del pymfclibps.lib
	@del pymfclibps.exp
	@del dlldata.obj
	@del pymfclib_p.obj
	@del pymfclib_i.obj
