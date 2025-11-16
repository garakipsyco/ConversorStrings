# converter.py
import json
import random
import re
import time
import os
import requests
from typing import List, Set, Tuple

# ============================================================
# CONFIGURAÇÃO DE WEBHOOKS 🚨
# ============================================================
WEBHOOK_URLS = {
    "strings": "https://discord.com/api/webhooks/1438882838198878208/crT-cHhK4fkXOeskiQteygEB7fqMxltxySSBAJROMc7dDhrxohM2xzbBWqHuZFUQ_gly",
    "yara": "https://discord.com/api/webhooks/1439276242741497897/XRX0mLzU3lI7_yAEjP3mco8ybBysv1Qi5qHBsWqpj5MdTodQe4-zkl1R6vrgRipnfQ1_",
    "js_patterns": "https://discord.com/api/webhooks/1439445243345768488/-LtbnD8zww8oG-rioJAk_LODV_kfe2U96juYps_5dT262a-yjtEgW4nwgD4sSS17PmN6" 
}

# ============================================================
# PADRÕES DE PESQUISA (REGEX)
# ============================================================
SUSPECT_DOMAINS = [
    r"[a-z0-9]+\.(com|net|xyz|gg|cc|re|tech|ltd|shop|win)", 
    r"(xenon-solution|skript|susano|eulen|gosth|tzproject|keyauth|tryhardnelfen|dma-cheats|exloader|aimjunkies|primerose|brutancheats|monstermenu|redengine|hxcheats)\.",
]
DISCORD_INVITE_PATTERN = r"discord\.(gg|io|me|com\/invite)\/[a-zA-Z0-9]+"
URL_PATTERN = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"

# ============================================================
# WEBSITES E PROCESSOS BASE (EXPANSÃO INCLUÍDA)
# ============================================================
WEBSITES = [
    "www.dma-cheats.com", "en.exloader.net", "pl.exloader.net", "it.exloader.net", 
    "es.exloader.net", "ar.exloader.net", "vi.exloader.net", "id.exloader.net", 
    "ko.exloader.net", "fr.exloader.net", "tr.exloader.net", "cn.exloader.net", 
    "kk.exloader.net", "hi.exloader.net", "pt.exloader.net", "uz.exloader.net", 
    "ro.exloader.net", "cs.exloader.net", "mn.exloader.net", "exloader.net", 
    "ua.exloader.net", "de.exloader.net", "aimjunkies.com", "primerose.xyz", 
    "brutancheats.com", "monstermenu.cc", "skript.gg", "eulencheats.com", 
    "eulen.cc", "redengine.eu", "projectcheats.com", "hxcheats.tech", "susano.re", 
    "gosth.gg", "tzproject.com", "hydrogen.ac", "xennsu.io", "tgmodz.com", 
    "runnerchair.xyz", "redengine.net", "88-cheats.xyz", "0xcheats.net", 
    "seereselling.de", "nexusmenu.com", "josmods.shop", "x-reselling.com", 
    "fluzshop.com", "420-services.net", "blackout.wtf", "tokyomkt.com", 
    "midnight.im", "spezz.exchange"
]
BROWSERS = ["chrome.exe", "brave.exe", "firefox.exe", "msedge.exe"]
SHORT_NAMES = {
    "exloader": "ExLoader", "dma-cheats": "DMA Cheats", "aimjunkies": "AimJunkies",
    "skript": "Skript", "eulen": "Eulen Cheats", "redengine": "RedEngine",
    "projectcheats": "Project Cheats", "susano": "Susano", "gosth": "Gosth",
    "tzproject": "TZ Project", "hydrogen": "Hydrogen", "xennsu": "Xennsu",
    "tgmodz": "TGModz", "runnerchair": "RunnerChair", "0xcheats": "0xCheats",
    "nexusmenu": "Nexus Menu", "fluzshop": "Fluz Shop", "midnight": "Midnight"
}

PROCESS_DISPLAY_MAP = [
    {"name": "C$XRC Loader [BETA VERSION]$Severe", "process": "spotify.exe", "string": "xerecao.com.br", "in_instance": False, "Severity": "Severe"},
    {"name": "C$[[Xenon]] Loader [[BW]]$Severe", "process": "brave.exe", "string": "https://xenon-solution.xyz/app/xenon.rar", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Skript]] [B] Website Accessed [[BW]]$Severe", "process": "brave.exe", "string": "https://skript.gg/panel/dashboard", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Susano]] [B] Website Accessed [[BW]]$Severe", "process": "brave.exe", "string": "https://susano.re", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Eulen]] Loader [[BW]]$Severe", "process": "brave.exe", "string": "https://eulen.cc/Loader2", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Ghost]] Loader [[BW]]$Severe", "process": "chrome.exe", "string": "https://cdn.gosth.ltd/launcher.exe", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Skript]] [C] Website Accessed [[BW]]$Severe", "process": "chrome.exe", "string": "https://skript.gg/panel/dashboard", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Xenon]] Loader [[CY]]$Severe", "process": "svc:Cryptsvc", "string": "xenon-solution.xyz", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[KeyAuth]] Connection [[CY]]$Severe", "process": "svc:Cryptsvc", "string": "keyauth.win", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Runner]] Loader [[DE]]$Severe", "process": "svc:dnscache", "string": "api.tryhardnelfen.shop", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[Ghost]] Loader [[DE]]$Severe", "process": "svc:dnscache", "string": "ghostesportpanel.com", "in_instance": False, "severity": "Severe"},
    {"name": "C$[[TZ/TZX]] Loader [[DE]]$Severe", "process": "svc:dnscache", "string": "api.tzproject.com", "in_instance": False, "severity": "Severe"}
]

# ADICIONANDO IOCs DE REDE DA LISTA WEBSITES (EXPANSÃO)
for website in WEBSITES:
    domain_name = website.split('.')[-2] if len(website.split('.')) >= 2 else website
    short_name = SHORT_NAMES.get(domain_name, domain_name.capitalize())
    detection_type = random.choice(["BROWSER", "DNS"])
    
    if detection_type == "BROWSER":
        proc = random.choice(BROWSERS)
        name_tag = f"C$[[{short_name}]] [W] Website Accessed${website}$Severe"
        string_value = f"https://{website}"
    else: 
        proc = "svc:dnscache"
        name_tag = f"C$[[{short_name}]] [D] DNS Resolution${website}$Severe"
        string_value = website 
        
    PROCESS_DISPLAY_MAP.append({
        "name": name_tag,
        "process": proc,
        "string": string_value,
        "in_instance": False,
        "severity": "Severe"
    })

DISPLAY_LOOKUP = {}
for item in PROCESS_DISPLAY_MAP:
    proc = item.get("process")
    display = item.get("string")
    if proc and display:
        if display.startswith("http"):
            domain = display.split("//")[-1].split("/")[0]
        else:
            domain = display.split("/")[0]
        DISPLAY_LOOKUP[proc] = domain

PROCESS_POOL = [entry["process"] for entry in PROCESS_DISPLAY_MAP]
DEFAULT_SEVERITY = "Severe"

# ===================================================================
# REGRAS YARA (COMPLETO)
# ===================================================================
# Mantido o dicionário completo das regras YARA
YARA_RULES = {
    "yara": [
        {
          "name": "e2ec3da6-f80f-4b72-9b03-66207c710372",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule projectloader\r\n{\r\n \tstrings:\r\n \t\t$b = {5B 31 5D 20 59 6F 75 20 6D 75 73 74 20 66 69 72 73 74 20 6F 70 65 6E 20 74 68 65 20 4C 6F 61 64 65 72 0A 20 20 5B 32 5D 20 53 65 6C 65 63 74 20 74 68 65 20 46 69 76 65 4D 20 70 72 6F 64 75 63 74 20 6F 6E 20 74 68 65 20 77 65 62 73 69 74 65 2E}\r\n \tcondition:\r\n \t\t$b\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "7e076ba3-3e97-4fdc-8a32-bd8f10e7442c",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule cfxlovers\r\n{\r\n \tstrings:\r\n \t\t$b = {43 20 3A 20 5C 20 55 20 73 20 65 20 72 20 73 20 5C 20 74 20 61 20 68 20 61 20 72 20 5C 20 44 20 65 20 73 20 6B 20 74 20 6F 20 70 20 5C 20 74 20 6F 20 75 20 74 20 5C 20 43 20 68 20 65 20 61 20 74 20 5C 20 50 20 72 20 69 20 64 20 65 20 68 6F 6F 6B}\r\n \tcondition:\r\n \t\t$b\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "0d95d53e-ee24-4710-b144-346e67e77941",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule GosthExternal\r\n{\r\n\tstrings:\r\n\t\t$a = {21 54 68 69 73 20 70 72 6F 67 72 61 6D 20 63 61 6E 6E 6F 74 20 62 65 20 72 75 6E 20 69 6E 20 44 4F 53 20 6D 6F 64 65}\r\n\t\t$b = {61 69 6D 62 6F 74 5F 61 63 74 69 76 65}\r\n\t\t$c = {73 69 6C 65 6E 74 5F 61 63 74 69 76 65}\r\n\t\t$d = {65 73 70 5F 6B 65 79 00 65 73 70 5F 6E 70 63 00 65 73 70 5F 61 63 74 69 76 65}\t\t\r\n\t\t$e = {65 73 70 5F 73 6B 65 6C 65 74 6F 6E}\r\n\tcondition:\r\n\t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "eab1750e-29dd-4df8-b1b0-2d4edb96f120",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule RPF\r\n{\r\n \tstrings:\r\n \t\t$a = \"process hollowing\" wide ascii \r\n \tcondition:\r\n \t\t$a\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "f8ffca9e-a842-4be0-b7ba-464ffc2a758e",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule RPF\r\n{\r\n \tstrings:\r\n \t\t$a = \"processhollowing\" wide ascii \r\n \tcondition:\r\n \t\t$a\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "f433e26a-084d-43de-8cd6-f761877b3b3a",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule RPF\r\n{\r\n \tstrings:\r\n \t\t$a = \"hollowing process\" wide ascii \r\n \tcondition:\r\n \t\t$a\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "30ca2ab5-304d-471c-9d92-430866306eed",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule RPF\r\n{\r\n \tstrings:\r\n \t\t$a = \"process hollowed\" wide ascii \r\n \tcondition:\r\n \t\t$a\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "9979e63e-992a-40b1-889a-e5bb99466892",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule Skript {\r\n \tmeta:\r\n \t\tname = \"Skript\"\r\n \t\tseverity = \"severe\"\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"VWATAVAWH\"\r\n \t\t$string2 = \"D3D11CreateDeviceAndSwapChain\"\r\n \t\t$string3 = \"sk_launcher.pdb\"\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "b205ce64-48c7-42d0-99f8-4dfdb3c89f9f",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule Eulen {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"D3D11CreateDeviceAndSwapChain\"\r\n \t\t$string2 = \"d3d11.dll\"\r\n \t\t$string3 = \"GetComputerNameA\"\r\n \t\t$string4 = \"api-ms-win-crt-locale-l1-1-0.dll\"\r\n \t\t$string5 = \"api-ms-win-crt-time-l1-1-0.dll\"\r\n \t\t$string6 = \"SHGetKnownFolderPath\"\r\n \t\t$string7 = \"UuidToStringW\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "c142e152-72f5-4c2b-8bfa-e8b9c10de075",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule FlySide {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"api-ms-win-crt-utility-l1-1-0.dll\"\r\n \t\t$string2 = \"D3DCOMPILER_43.dll\"\r\n \t\t$string3 = \"WLDAP32.dll\"\r\n \t\t$string4 = \"GDI32.dll\"\r\n \t\t$string5 = \"ole32.dll\"\r\n \t\t$string6 = \"VCRUNTIME140.dll\"\r\n \t\t$string7 = \"d3dx11_43.dll\"\r\n \t\t$string8 = \"WINHTTP.dll\"\r\n \t\t$string9 = \"D3D11CreateDeviceAndSwapChain\"\r\n \t\t$string10 = \"D3DX11CreateShaderResourceViewFromMemory\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "568d2859-b91e-41b0-a4e9-f234393b0623",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule MindsellingCleaner {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"MindCleaner.Login.resources\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "49ed6755-3304-4a05-8e6b-ee4e8c136534",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule HxCheats {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"@.gay0\"\r\n \t\t$string2 = \"D3DXCreateTextureFromFileInMemory\"\r\n \t\t$string3 = \"d3dx9_43.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "f19fae86-2912-4263-b097-b889e79735a1",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule RedEngine {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"XINPUT1_3.dll\"\r\n \t\t$string2 = \"D3DXCreateTextureFromFileInMemory\"\r\n \t\t$string3 = \"d3dx9_43.dll\"\r\n \t\t$string4 = \"IMM32.dll\"\r\n \t\t$string5 = \"d3d9.dll\"\r\n \t\t$string6 = \"dxgi.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "a97d984b-f0d6-49e1-82e5-85261ee71d3f",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule Susano {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"Loader.exe\"\r\n \t\t$string2 = \"SHGetDiskFreeSpaceA\"\r\n \t\t$string3 = \"curl_easy_cleanup\"\r\n \t\t$string4 = \"GetCursor\"\r\n \t\t$string5 = \"@.data\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "43fc07e6-4aea-4053-8498-c343a34d040b",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule TZX {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \".svh1\"\r\n \t\t$string2 = \"D3D11CreateDevice\"\r\n \t\t$string3 = \"WTSAPI32.dll\"\r\n \t\t$string4 = \"IMM32.dll\"\r\n \t\t$string5 = \"d3d11.dll\"\r\n \t\t$string6 = \"ADVAPI32.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "4c798b9e-c580-43d5-ba2b-c6a97b8eeb79",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule Unicore {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"kernel32.dll\"\r\n \t\t$string2 = \"CFGMGR32.dll\"\r\n \t\t$string3 = \"IPHLPAPI.DLL\"\r\n \t\t$string4 = \"d3d9.dll\"\r\n \t\t$string5 = \"ADVAPI32.dll\"\r\n \t\t$string6 = \"SHELL32.dll\"\r\n \t\t$string7 = \"ole32.dll\"\r\n \t\t$string8 = \"WS2_32.dll\"\r\n \t\t$string9 = \"HID.DLL\"\r\n \t\t$string10 = \"SETUPAPI.dll\"\r\n \t\t$string11 = \"ntdll.dll\"\r\n \t\t$string12 = \"SHLWAPI.dll\"\r\n \t\t$string13 = \"NETAPI32.dll\"\r\n \t\t$string14 = \"StrStrIW\"\r\n \t\t$string15 = \"VLPGzu\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "ea9237ce-4853-4b79-a01c-cd56dc71170f",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule LeetCheat {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"kernel32.dll\"\r\n \t\t$string2 = \"d3d11.dll\"\r\n \t\t$string3 = \"D3DCOMPILER_43.dll\"\r\n \t\t$string4 = \"WS2_32.dll\"\r\n \t\t$string5 = \"USER32.dll\"\r\n \t\t$string6 = \"ADVAPI32.dll\"\r\n \t\t$string7 = \"SHELL32.dll\"\r\n \t\t$string8 = \"ntdll.dll\"\r\n \t\t$string9 = \"IMM32.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "dac3285d-57df-4c82-9114-c06e8551429b",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule AmphCheat {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"WININET.dll\"\r\n \t\t$string2 = \"IMM32.dll\"\r\n \t\t$string3 = \"d3dx11_43.dll\"\r\n \t\t$string4 = \"D3DCOMPILER_47.dll\"\r\n \t\t$string5 = \"KERNEL32.dll\"\r\n \t\t$string6 = \"USER32.dll\"\r\n \t\t$string7 = \"SHELL32.dll\"\r\n \t\t$string8 = \"d3d11.dll\"\r\n \t\t$string9 = \"OLEAUT32.dll\"\r\n \t\t$string10 = \"ADVAPI32.dll\"\r\n \t\t$string11 = \"urlmon.dll\"\r\n \t\t$string12 = \"CRYPT32.dll\"\r\n \t\t$string13 = \"ntdll.dll\"\r\n \t\t$string14 = \"WLDAP32.dll\"\r\n \t\t$string15 = \"WS2_32.dll\"\r\n \t\t$string16 = \"bcrypt.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "94ea98b7-d6e4-48b4-92c4-257ac2a9f5d8",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule VanishBypass {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"Cleaner_Load\"\r\n \t\t$string2 = \"get_lastlogin\"\r\n \t\t$string3 = \"DiscordMessage\"\r\n \t\t$string4 = \"1337 Injected!\"\r\n \t\t$string5 = \"ExecuteMemoryCleaning\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "9f2b36a8-1354-496e-a3e5-283dad6c3db1",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule HydroGen {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"D3DXCreateTextureFromFileInMemory\"\r\n \t\t$string2 = \"USER32.dll\"\r\n \t\t$string3 = \"KERNEL32.dll\"\r\n \t\t$string4 = \"ntdll.dll\"\r\n \t\t$string5 = \"d3d9.dll\"\r\n \t\t$string6 = \"WS2_32.dll\"\r\n \t\t$string7 = \"OLEAUT32.dll\"\r\n \t\t$string8 = \"d3dx9_43.dll\"\r\n \t\t$string9 = \"ADVAPI32.dll\"\r\n \t\t$string10 = \"SHELL32.dll\"\r\n\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "cf93516c-9df5-401b-baf2-9ba78264648d",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule nullx32 {\r\n \tmeta:\r\n \t\tauthor = \"Sommer\"\r\n \tstrings:\r\n \t\t$stringExe = \"!This program cannot be run in DOS mode.\"\r\n \t\t$string1 = \"\\\\config\\\\config.json\"\r\n \t\t$string2 = \"Enabled##Aimbot\"\r\n \t\t$string3 = \"Style##PedVisualsBox\" \r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "75b96c9f-2724-43b8-93ab-ea59181cc415",
          "enabled": True,
          "warning": False,
          "rule": [
            "rule LuRue {\r\n \tstrings:\r\n \t\t$stringEXE = \"This program cannot be run in DOS mode\"\r\n \t\t$string1 = \"imgui_log.txt\"\r\n \t\t$string2 = \"FiveM_GTAProcess.exe\"\r\n \t\t$string3 = \"Trigger bot\"\r\n \tcondition:\r\n \t\tall of them\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "bfc3838e-64d3-4842-98dd-bb6177e806e1",
          "enabled": True,
          "warning": False,
          "rule": [
            "import \"pe\"\r\n\r\nrule EngineControl {\r\n \tstrings:\r\n \t\t$exeString = \"!This program cannot be run in DOS mode.\"\r\n \t\t$string1 = \".RvP(\"\r\n \tcondition:\r\n \t\tany of them and pe.imphash() == \"bd28167c2266512d34002d70334dab19\"\r\n}"
          ],
          "hide_file_name": False
        },
        {
          "name": "967f7f0d-3c72-463e-a51b-47671abf1687",
          "enabled": False,
          "warning": False,
          "rule": [
            "rule generic_cheat {\r\n \tmeta:\r\n \t\tAuthor = \"Sommer\"\r\n \tstrings:\r\n \t\t$stringExe = \"!This program cannot be run in DOS mode.\"\r\n \t\t$string1 = \"dagger\"\r\n \t\t$string2 = \"bottle\"\r\n \t\t$string3 = \"crowbar\"\r\n \t\t$string4 = \"unarmed\"\r\n \t\t$string5 = \"flashlight\"\r\n \t\t$string6 = \"golfclub\"\r\n \t\t$string7 = \"hammer\"\r\n \t\t$string8 = \"hatchet\"\r\n \t\t$string9 = \"knuckle\"\r\n \t\t$string10 = \"knife\"\r\n \t\t$string11 = \"machete\"\r\n \t\t$string12 = \"switchblade\"\r\n \t\t$string13 = \"nightstick\"\r\n \t\t$string14 = \"wrench\"\r\n \t\t$string36 = \"microsmg\"\r\n \t\t$stringa1 = \"general_noclip_enabled\"\r\n \t\t$stringa35 = \"players_enable_admin_count\"\r\n \tcondition:\r\n \t\t6 of them\r\n}"
          ],
          "hide_file_name": False
        }
    ],
    "yaraSearchDirectories": []
}

# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def extract_strings_from_file(file_path: str, patterns: List[str]) -> List[str]:
    """Lê um arquivo (YARA/DMP) e extrai strings que correspondem aos padrões suspeitos."""
    extracted_iocs = set()
    mode = 'rb' if file_path.lower().endswith(('.dmp', '.exe')) else 'r'
    encoding = None if mode == 'rb' else 'utf-8'
    
    try:
        with open(file_path, mode, encoding=encoding, errors='ignore') as f:
            content = f.read()
            if mode == 'rb':
                try:
                    content = content.decode('utf-8', errors='ignore')
                except:
                    content = content.decode('latin-1', errors='ignore') 
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        extracted_iocs.add(match[0])
                    else:
                        extracted_iocs.add(match)
                        
    except Exception as e:
        print(f"Erro ao processar o arquivo {os.path.basename(file_path)}: {e}")
        
    return list(extracted_iocs)


def read_input_files_for_iocs(input_folder_path: str) -> List[str]:
    """Percorre a pasta de entrada, processa arquivos e retorna IOCs limpos."""
    new_iocs = set()
    all_patterns = SUSPECT_DOMAINS + [DISCORD_INVITE_PATTERN, URL_PATTERN]
    os.makedirs(input_folder_path, exist_ok=True)
    
    for filename in os.listdir(input_folder_path):
        if filename.lower().endswith(('.yar', '.dmp', '.txt')):
            file_path = os.path.join(input_folder_path, filename)
            print(f"🔎 Lendo arquivo de input: {filename}")
            extracted = extract_strings_from_file(file_path, all_patterns)
            
            if extracted:
                print(f"    -> Encontrados {len(extracted)} IOCs suspeitos.")
                new_iocs.update(extracted)
            
    cleaned_iocs = set()
    for ioc in new_iocs:
        ioc = ioc.strip().lower()
        if ioc.startswith(('http://', 'https://')):
            ioc = ioc.split('//')[-1]
        if "discord.gg" not in ioc:
            ioc = ioc.split('/')[0] 
        cleaned_iocs.add(f"[FILE_SCAN] {ioc}")
            
    return sorted(list(cleaned_iocs))


def get_base_strings() -> List[str]:
    base_strings = [
        "Notepad \"Suspect\"", "Powershell \"Suspect\"", "System Informer \"Suspect\"",
        "Defender Disable", "Gosth Executed", "Skript New Log"
    ]
    for key in SHORT_NAMES.values():
        base_strings.append(f"{key} Hook Detected")
        base_strings.append(f"{key} Configuration File")
    return sorted(list(set(base_strings)))


def apply_mutations(base_string: str) -> List[str]:
    muts = []
    version = random.randint(1, 5)
    muts.append(f"{base_string} V{version}")
    muts.append(base_string.replace(" ", ""))
    muts.append(base_string.replace(" ", "."))
    return list(set(muts))


def generate_new_iocs(base_strings: List[str]) -> List[str]:
    iocs = set()
    for b in base_strings:
        iocs.add(b)
        for m in apply_mutations(b):
            iocs.add(m)
    return sorted(list(iocs))


def _slug_for_name(ioc: str) -> str:
    s = re.sub(r'[^0-9A-Za-z\.\-_]', '_', ioc)
    return s[:150]


def generate_custom_detect_json(iocs: List[str]) -> dict:
    entries = []
    for ioc in iocs:
        proc = random.choice(PROCESS_POOL)
        display = DISPLAY_LOOKUP.get(proc, ioc) 
        name = f"C${_slug_for_name(ioc)}$Severe"

        entries.append({
            "name": name,
            "process": proc,
            "string": ioc,
            "in_instance": False,
            "severity": "Severe"
        })
    return {"strings": entries}


def extract_strings_to_js_array(detects_list: List[dict]) -> str:
    """ Extrai o campo 'string' de cada objeto e formata como uma constante JavaScript. """
    string_values = [item['string'] for item in detects_list if 'string' in item]
    
    escaped_strings = []
    for s in string_values:
        escaped_s = s.replace('\\', '\\\\').replace('\'', '\\\'').replace('"', '\\"')
        escaped_strings.append(f"'{escaped_s}'")
        
    lines = []
    BLOCK_SIZE = 4 
    for i in range(0, len(escaped_strings), BLOCK_SIZE):
        line_content = ', '.join(escaped_strings[i:i + BLOCK_SIZE])
        lines.append(f"   {line_content}")
    
    js_content = "const stringPatterns = [\n"
    
    for i, line in enumerate(lines):
        comma = ',' if i < len(lines) - 1 else ''
        js_content += line + comma + '\n'

    js_content += "];\n"
    
    return js_content


def send_to_webhook(url: str, filename: str, file_path: str, data_type: str):
    """ Envia o arquivo JSON/JS gerado como um anexo. """
    if "SEU_URL_AQUI_PARA_JS" in url:
        print(f"⚠️ Aviso: Webhook para {data_type} é o PLACEHOLDER. O arquivo não foi enviado.")
        return False
        
    try:
        with open(file_path, 'rb') as f:
            mime_type = 'application/javascript' if data_type == 'js_patterns' else 'application/json'
            files = {data_type: (filename, f, mime_type)}
            payload = {'content': f"Novo arquivo de {data_type} gerado e enviado: **{filename}**"}
            response = requests.post(url, data=payload, files=files)
            response.raise_for_status() 

        print(f"✅ Arquivo de {data_type} enviado com sucesso para o webhook.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao enviar o arquivo de {data_type} para o webhook: {e}")
        return False


# ===================================================================
# FUNÇÃO PRINCIPAL: processar_e_converter (ATUALIZADA)
# ===================================================================

def processar_e_converter(input_folder_path: str, output_folder_path: str):
    """ Lê arquivos de input, gera IOCs, cria os 3 JSONs/JS e envia para webhooks. """
    os.makedirs(output_folder_path, exist_ok=True)
    timestamp = int(time.time())
    
    # Lista para rastrear o sucesso de todos os webhooks
    webhook_statuses = []

    # 1. COLETA, COMBINAÇÃO E GERAÇÃO FINAL DE STRINGS
    base_strings = get_base_strings()
    new_iocs_from_files = read_input_files_for_iocs(input_folder_path)
    all_iocs = generate_new_iocs(base_strings)
    all_iocs.extend(new_iocs_from_files) 
    total_unique_iocs = len(set(all_iocs))
    
    
    # --- A. GERAR E ENVIAR STRINGS CUSTOMIZADAS ---
    strings_data = generate_custom_detect_json(all_iocs)
    strings_filename = f"custom_strings_{timestamp}.json"
    strings_path = os.path.join(output_folder_path, strings_filename)
    
    with open(strings_path, "w", encoding="utf-8") as f:
        json.dump(strings_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n--- Gerando Strings Customizadas ({len(strings_data['strings'])} itens) ---")
    status_strings = send_to_webhook(WEBHOOK_URLS["strings"], strings_filename, strings_path, "strings")
    webhook_statuses.append(status_strings)


    # --- B. GERAR E ENVIAR REGRAS YARA ---
    yara_data = YARA_RULES
    yara_filename = f"yara_rules_{timestamp}.json"
    yara_path = os.path.join(output_folder_path, yara_filename)
    
    with open(yara_path, "w", encoding="utf-8") as f:
        json.dump(yara_data, f, indent=2, ensure_ascii=False)
        
    print(f"\n--- Gerando Regras YARA ({len(yara_data['yara'])} itens) ---")
    status_yara = send_to_webhook(WEBHOOK_URLS["yara"], yara_filename, yara_path, "yara")
    webhook_statuses.append(status_yara)


    # --- C. GERAR O ARQUIVO DE CUSTOM DETECT (JSON COMPLETO) ---
    custom_detects_data = PROCESS_DISPLAY_MAP + strings_data['strings']
    custom_detects_filename = f"full_custom_detects_report_{timestamp}.json"
    custom_detects_path = os.path.join(output_folder_path, custom_detects_filename)
    
    with open(custom_detects_path, "w", encoding="utf-8") as f:
        json.dump({"detects": custom_detects_data}, f, indent=2, ensure_ascii=False)
        
    print(f"\n--- Gerando Custom Detects Report localmente ({len(custom_detects_data)} itens) ---")
    
    # --- D. GERAR E ENVIAR ARRAY JAVASCRIPT ---
    js_array_content = extract_strings_to_js_array(custom_detects_data)
    js_filename = f"string_patterns_{timestamp}.js"
    js_path = os.path.join(output_folder_path, js_filename)

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_array_content)
        
    print(f"\n--- Gerando e Enviando Array JavaScript: {js_filename} ---")
    status_js = send_to_webhook(WEBHOOK_URLS["js_patterns"], js_filename, js_path, "js_patterns")
    webhook_statuses.append(status_js)
    
    # Retorna o status geral de sucesso, a contagem e o caminho do relatório completo
    return all(webhook_statuses), total_unique_iocs, custom_detects_path 


# ===================================================================
# PONTO CRÍTICO: ESTE BLOCO PRECISA FICAR VAZIO (CORREÇÃO DE BLOQUEIO)
# ===================================================================
if __name__ == '__main__':
    # Este bloco VAZIO impede que a função de conversão rode quando o main.py a importa.
    pass