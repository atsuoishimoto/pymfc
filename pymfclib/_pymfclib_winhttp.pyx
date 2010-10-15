# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"


cdef extern from "Winhttp.h":
    ctypedef void *HINTERNET 
    
    HINTERNET WinHttpOpen(LPCWSTR pwszUserAgent, DWORD dwAccessType, LPCWSTR pwszProxyName, LPCWSTR pwszProxyBypass, DWORD dwFlags)
    BOOL WinHttpCloseHandle(HINTERNET hInternet)
    
    ctypedef struct WINHTTP_CURRENT_USER_IE_PROXY_CONFIG:
        BOOL fAutoDetect
        LPWSTR lpszAutoConfigUrl
        LPWSTR lpszProxy
        LPWSTR lpszProxyBypass
    
    BOOL WinHttpGetIEProxyConfigForCurrentUser(WINHTTP_CURRENT_USER_IE_PROXY_CONFIG* pProxyConfig)

    int WINHTTP_AUTOPROXY_AUTO_DETECT, WINHTTP_AUTOPROXY_CONFIG_URL, WINHTTP_AUTOPROXY_RUN_INPROCESS
    int WINHTTP_AUTO_DETECT_TYPE_DHCP, WINHTTP_AUTO_DETECT_TYPE_DNS_A
 
    ctypedef struct WINHTTP_AUTOPROXY_OPTIONS:
        DWORD dwFlags
        DWORD dwAutoDetectFlags
        LPCWSTR lpszAutoConfigUrl
        LPVOID lpvReserved
        DWORD dwReserved
        BOOL fAutoLogonIfChallenged

    int WINHTTP_ACCESS_TYPE_NO_PROXY, WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, WINHTTP_ACCESS_TYPE_NAMED_PROXY, WINHTTP_FLAG_ASYNC

    ctypedef struct WINHTTP_PROXY_INFO:
        DWORD dwAccessType
        LPWSTR lpszProxy
        LPWSTR lpszProxyBypass

    BOOL WinHttpGetProxyForUrl(HINTERNET hSession, LPCWSTR lpcwszUrl, WINHTTP_AUTOPROXY_OPTIONS* pAutoProxyOptions, WINHTTP_PROXY_INFO* pProxyInfo)


cdef class CurrentUserIEProxyConfig:
    cdef public object autodetect
    cdef public object autoconfigurl
    cdef public object proxy
    cdef public object proxybypass

cdef class ProxyInfo:
    cdef public object noproxy
    cdef public object proxy
    cdef public object proxybypass


def getIEProxyConfigForCurrentUser():
    cdef WINHTTP_CURRENT_USER_IE_PROXY_CONFIG ieconfig
    cdef CurrentUserIEProxyConfig ret
    
    memset(&ieconfig, 0, sizeof(ieconfig))
    if WinHttpGetIEProxyConfigForCurrentUser(&ieconfig):
        ret = CurrentUserIEProxyConfig()
        ret.autodetect = ieconfig.fAutoDetect
        try:
            if ieconfig.lpszAutoConfigUrl:
                ret.autoconfigurl = _fromWideChar(ieconfig.lpszAutoConfigUrl)
            if ieconfig.lpszProxy:
                ret.proxy = _fromWideChar(ieconfig.lpszProxy)
            if ieconfig.lpszProxyBypass:
                ret.proxybypass = _fromWideChar(ieconfig.lpszProxyBypass)
        finally:
            if ieconfig.lpszAutoConfigUrl:
                GlobalFree(ieconfig.lpszAutoConfigUrl)
            if ieconfig.lpszProxy:
                GlobalFree(ieconfig.lpszProxy)
            if ieconfig.lpszProxyBypass:
                GlobalFree(ieconfig.lpszProxyBypass)
        return ret


cdef class WinHTTPSession:
    cdef HINTERNET hInternet
    def __init__(self, agent):
        cdef HINTERNET handle
        handle = WinHttpOpen(PyUnicode_AsUnicode(agent), WINHTTP_ACCESS_TYPE_NO_PROXY, NULL, NULL, 0)
        if not handle:
            pymRaiseWin32Err()
        self.hInternet = handle
    
    def __dealloc__(self):
        if self.hInternet:
            WinHttpCloseHandle(self.hInternet)
            self.hInternet = NULL

    def getProxyForUrl(self, url, configurl):
        cdef WINHTTP_AUTOPROXY_OPTIONS autoopt
        cdef WINHTTP_PROXY_INFO proxyinfo
        cdef ProxyInfo ret
        
        memset(&autoopt, 0, sizeof(autoopt))
        memset(&proxyinfo, 0, sizeof(proxyinfo))
        
        if configurl:
            autoopt.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT | WINHTTP_AUTOPROXY_CONFIG_URL
            autoopt.lpszAutoConfigUrl = PyUnicode_AsUnicode(configurl)
        else:
            autoopt.dwFlags = WINHTTP_AUTOPROXY_AUTO_DETECT

        autoopt.dwAutoDetectFlags = WINHTTP_AUTO_DETECT_TYPE_DHCP | WINHTTP_AUTO_DETECT_TYPE_DNS_A
        autoopt.fAutoLogonIfChallenged = 1

        if WinHttpGetProxyForUrl(self.hInternet, PyUnicode_AsUnicode(url), &autoopt, &proxyinfo):
            ret = ProxyInfo()
            ret.noproxy = proxyinfo.dwAccessType == WINHTTP_ACCESS_TYPE_NO_PROXY

            try:
                if proxyinfo.lpszProxy:
                    ret.proxy = _fromWideChar(proxyinfo.lpszProxy)
                if proxyinfo.lpszProxyBypass:
                    ret.proxybypass = _fromWideChar(proxyinfo.lpszProxyBypass)
            finally:
                if proxyinfo.lpszProxy:
                    GlobalFree(proxyinfo.lpszProxy)
                if proxyinfo.lpszProxyBypass:
                    GlobalFree(proxyinfo.lpszProxyBypass)
            return ret
            

