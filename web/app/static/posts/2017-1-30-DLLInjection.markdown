---
layout: post
title:  "DLL注入笔记"
date:   2017-01-30 11:49:45 +0200
categories: re
published: true
---
## 0x00 什么是DLL注入？

DLL注入是指向运行中的程序强制插入特定的DLL文件。DLL被加载到程序中后，会自动执行DLLMain()函数，用户可以把代码放到DllMain()函数中，这样每当该DLL文件被加载时，代码就会得到执行。利用该特性，可以实现：

- 改善功能和修复BUG
- 消息钩取
- API钩取
- 实现各种监视，管理程序
- 编写恶意代码

对于DLL注入的实现主要有以下方法：

1. 创建远程线程（CreateRemoteThread()API）
2. 使用注册表（AppInit_DLLs值）
3. 消息钩取（SetWindowsHookEx()API）

个人感觉第三种不怎么好用，就不在这篇笔记中记录了。 

## 0x01 使用创建远程线程实现DLL注入

原理就是利用CreateRemoteThread()API在目标进程中执行LoadLibrary()加载目标DLL。  代码如下：

```c
#include "windows.h"
#include "tchar.h"

BOOL SetPrivilege(LPCTSTR lpszPrivilege, BOOL bEnablePrivilege) 
{
    TOKEN_PRIVILEGES tp;
    HANDLE hToken;
    LUID luid;

    if( !OpenProcessToken(GetCurrentProcess(),
                          TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, 
                          &hToken) )
    {
        _tprintf(L"OpenProcessToken error: %u\n", GetLastError());
        return FALSE;
    }

    if( !LookupPrivilegeValue(NULL,           // lookup privilege on local system
                              lpszPrivilege,  // privilege to lookup 
                              &luid) )        // receives LUID of privilege
    {
        _tprintf(L"LookupPrivilegeValue error: %u\n", GetLastError() ); 
        return FALSE; 
    }

    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    if( bEnablePrivilege )
        tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    else
        tp.Privileges[0].Attributes = 0;

    // Enable the privilege or disable all privileges.
    if( !AdjustTokenPrivileges(hToken, 
                               FALSE, 
                               &tp, 
                               sizeof(TOKEN_PRIVILEGES), 
                               (PTOKEN_PRIVILEGES) NULL, 
                               (PDWORD) NULL) )
    { 
        _tprintf(L"AdjustTokenPrivileges error: %u\n", GetLastError() ); 
        return FALSE; 
    } 

    if( GetLastError() == ERROR_NOT_ALL_ASSIGNED )
    {
        _tprintf(L"The token does not have the specified privilege. \n");
        return FALSE;
    } 

    return TRUE;
}

BOOL InjectDll(DWORD dwPID, LPCTSTR szDllPath)
{
    HANDLE hProcess = NULL, hThread = NULL;
    HMODULE hMod = NULL;
    LPVOID pRemoteBuf = NULL;
    DWORD dwBufSize = (DWORD)(_tcslen(szDllPath) + 1) * sizeof(TCHAR);
    LPTHREAD_START_ROUTINE pThreadProc;

    // #1. 通过dwPID获取到目标进程句柄
    if ( !(hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwPID)) )
    {
        _tprintf(L"OpenProcess(%d) failed!!! [%d]\n", dwPID, GetLastError());
        return FALSE;
    }

    // #2. 在目标进程中分配DLL路径长度的内存空间
    pRemoteBuf = VirtualAllocEx(hProcess, NULL, dwBufSize, MEM_COMMIT, PAGE_READWRITE);

    // #3. 将DLL路径写入DLL分配好的空间中
    WriteProcessMemory(hProcess, pRemoteBuf, (LPVOID)szDllPath, dwBufSize, NULL);

    // #4. 获取LoadLibraryW()在内存中的地址
    hMod = GetModuleHandle(L"kernel32.dll");
    pThreadProc = (LPTHREAD_START_ROUTINE)GetProcAddress(hMod, "LoadLibraryW");
    
    // #5. 在目标进程中创建线程，加载目标DLL
    hThread = CreateRemoteThread(hProcess, NULL, 0, pThreadProc, pRemoteBuf, 0, NULL);
    WaitForSingleObject(hThread, INFINITE); 

    CloseHandle(hThread);
    CloseHandle(hProcess);

    return TRUE;
}

int _tmain(int argc, TCHAR *argv[])
{
    if( argc != 3)
    {
        _tprintf(L"USAGE : %s <pid> <dll_path>\n", argv[0]);
        return 1;
    }

    // change privilege
    if( !SetPrivilege(SE_DEBUG_NAME, TRUE) )
        return 1;

    // inject dll
    if( InjectDll((DWORD)_tstol(argv[1]), argv[2]) )
        _tprintf(L"InjectDll(\"%s\") success!!!\n", argv[2]);
    else
        _tprintf(L"InjectDll(\"%s\") failed!!!\n", argv[2]);

    return 0;
}
```

在上面的代码中有几点是需要注意的：

1. VirtualAllocEx()申请到的地址是在目标进程中的内存空间中的。
2. kernel32.dll在Windows系统中，每个进程对它的加载地址都是相同的，所以可以在注入时直接获取到它的地址。

## 0x02 利用注册表实现DLL注入

Windwos操作系统的注册表中默认提供了AppInit_DLLs与LoadAppInit_DLLs两个注册表项。

在注册表编辑器中，将要注入的DLL路径字符串写入AppInit_DLLs项目，然后把LoadAppInit_DLLs的项目值设置为1。重启后，指定DLL会注入所有运行进程。