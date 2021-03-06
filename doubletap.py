#!/usr/bin/env python
import subprocess
import netifaces as ni
import re
import multiprocessing
from multiprocessing import Process, Queue
import os
import time
import fileinput
import atexit
import sys
import socket
import requests

##Change me if needed

myip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']

dirs = "/root/Desktop/"

##Stop changing shit here

start = time.time()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Creates a function for multiprocessing.
def multProc(targetin, scanip, port):
    jobs = []
    p = multiprocessing.Process(target=targetin, args=(scanip,port))
    jobs.append(p)
    p.start()
    return

# Functions for service specific connections.
def connect_to_port(ip_address, port, service):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_address, int(port)))
    banner = s.recv(1024)

    if service == "ftp":
        s.send("USER anonymous\r\n")
        user = s.recv(1024)
        s.send("PASS anonymous\r\n")
        password = s.recv(1024)
        total_communication = banner + "\r\n" + user + "\r\n" + password
        write_to_file(ip_address, "ftp-connect", total_communication)
    elif service == "smtp":
        total_communication = banner + "\r\n"
        write_to_file(ip_address, "smtp-connect", total_communication)
    elif service == "ssh":
        total_communication = banner
        write_to_file(ip_address, "ssh-connect", total_communication)
    elif service == "pop3":
        s.send("USER root\r\n")
        user = s.recv(1024)
        s.send("PASS root\r\n")
        password = s.recv(1024)
        total_communication = banner +  user +  password
        write_to_file(ip_address, "pop3-connect", total_communication)
    s.close()


#Functions for writing into templates
def write_to_file(ip_address, enum_type, data):
    file_path_linux = "%s%s/%s-linux-exploit-steps.md" % (dirs, ip_address, ip_address)
    file_path_windows = "%s%s/%s-windows-exploit-steps.md" % (dirs, ip_address, ip_address)
    paths = [file_path_linux, file_path_windows]
    print bcolors.OKGREEN + "INFO: Writing " + enum_type + " to template files:\n " + file_path_linux + "   \n" + file_path_windows + bcolors.ENDC

    for path in paths:
#        if enum_type == "portscan":
#            subprocess.check_output("replace INSERTTCPSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "dirb":
            subprocess.check_output("replace INSERTDIRBSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "dirbssl":
            subprocess.check_output("replace INSERTDIRBSSLSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "nikto":
            subprocess.check_output("replace INSERTNIKTOSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ftp-connect":
            subprocess.check_output("replace INSERTFTPTEST \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "smtp-connect":
            subprocess.check_output("replace INSERTSMTPCONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ssh-connect":
            subprocess.check_output("replace INSERTSSHCONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "pop3-connect":
            subprocess.check_output("replace INSERTPOP3CONNECT \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "curl":
            subprocess.check_output("replace INSERTCURLHEADER \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "wig":
            subprocess.check_output("replace INSERTWIGSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "wigssl":
            subprocess.check_output("replace INSERTWIGSSLSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "smbmap":
            subprocess.check_output("replace INSERTSMBMAP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "rpcmap":
            subprocess.check_output("replace INSERTRPCMAP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "samrdump":
            subprocess.check_output("replace INSERTSAMRDUMP \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "vulnscan":
            subprocess.check_output("replace INSERTVULNSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "nfsscan":
            subprocess.check_output("replace INSERTNFSSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "ssl-scan":
            subprocess.check_output("replace INSERTSSLSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "parsero":
            subprocess.check_output("replace INSERTROBOTS \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "sshscan":
            subprocess.check_output("replace INSERTSSHBRUTE \"" + str(data) + "\"  -- " + path, shell=True)
        if enum_type == "fulltcpscan":
            subprocess.check_output("replace INSERTFULLTCPSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "udpscan":
            subprocess.check_output("replace INSERTUDPSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "waf":
            subprocess.check_output("replace INSERTWAFSCAN \"" + data + "\"  -- " + path, shell=True)
        if enum_type == "wafssl":
            subprocess.check_output("replace INSERTWAFSSLSCAN \"" + data + "\"  -- " + path, shell=True)
    return

#Scanning functions
def dirb(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting dirb scan for " + ip_address + ":" + port + bcolors.ENDC
    DIRBSCAN = "gobuster -u %s://%s:%s -e -f -n -w /usr/share/wordlists/dirb/common.txt -P /opt/doubletap-git/wordlists/quick_hit.txt -U /opt/doubletap-git/wordlists/quick_hit.txt -t 20 | grep -o 'http.*' | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' | tee -a %s%s/webapp_scans/dirb-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #DIRBSCAN = "dirb %s://%s:%s -S -o" + dirs + "/dirb-%s.txt" % (url_start, ip_address, port, ip_address, ip_address)
    results_dirb = subprocess.check_output(DIRBSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with DIRB-scan for " + ip_address + bcolors.ENDC
    print results_dirb
    write_to_file(ip_address, "dirb", results_dirb)
    return

def dirbssl(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting dirb scan for " + ip_address + ":" + port + bcolors.ENDC
    DIRBSCAN = "gobuster -u %s://%s:%s -e -f -n -w /usr/share/wordlists/dirb/common.txt -P /opt/doubletap-git/wordlists/quick_hit.txt -U /opt/doubletap-git/wordlists/quick_hit.txt -t 20 | grep -o 'http.*' | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' | tee -a %s%s/webapp_scans/dirb-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #DIRBSCAN = "dirb %s://%s:%s -S -o" + dirs + "/dirb-%s.txt" % (url_start, ip_address, port, ip_address, ip_address)
    results_dirb = subprocess.check_output(DIRBSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with DIRB_SSL-scan for " + ip_address + bcolors.ENDC
    print results_dirb
    write_to_file(ip_address, "dirbssl", results_dirb)
    return

def wig(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting wig scan for " + ip_address + bcolors.ENDC
    WIGSCAN = "wig-git -t 20 -u %s://%s:%s -q -d | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' | tee -a %s%s/webapp_scans/wig-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #WIGSCAN = "wig-git -t 20 -l %s%s/webapp_scans/http-dirb-%s.txt --no_cache_load --no_cache_save -w %s%s/webapp_scans/%s-wig-%s.txt | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g'" % (dirs, ip_address, ip_address, dirs, ip_address, url_start, ip_address)
    results_wig = subprocess.check_output(WIGSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with WIG-scan for " + ip_address + bcolors.ENDC
    print results_wig
    write_to_file(ip_address, "wig", results_wig)
    return

def wigssl(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting wig scan for " + ip_address + bcolors.ENDC
    WIGSCAN = "wig-git -t 20 -u %s://%s:%s -q -d | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' | tee -a %s%s/webapp_scans/wig-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #WIGSCAN = "wig-git -t 20 -l %s%s/webapp_scans/http-dirb-%s.txt --no_cache_load --no_cache_save -w %s%s/webapp_scans/%s-wig-%s.txt | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g'" % (dirs, ip_address, ip_address, dirs, ip_address, url_start, ip_address)
    results_wig = subprocess.check_output(WIGSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with WIG-scan for " + ip_address + bcolors.ENDC
    print results_wig
    write_to_file(ip_address, "wigssl", results_wig)
    return

def parsero(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting parsero scan for " + ip_address + bcolors.ENDC
    ROBOTSSCAN = "parsero-git -o -u %s://%s:%s | grep OK | grep -o 'http.*' | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' | tee -a %s%s/webapp_scans/dirb-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    results_parsero = subprocess.check_output(ROBOTSSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with PARSERO-scan for " + ip_address + bcolors.ENDC
    print results_parsero
    write_to_file(ip_address, "parsero", results_parsero)
    return

def waf(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting firewall scan for " + ip_address + bcolors.ENDC
    WAFSCAN = "wafw00f %s://%s:%s -a | tee -a %s%s/webapp_scans/waf-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #WIGSCAN = "wig-git -t 20 -l %s%s/webapp_scans/http-dirb-%s.txt --no_cache_load --no_cache_save -w %s%s/webapp_scans/%s-wig-%s.txt | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g'" % (dirs, ip_address, ip_address, dirs, ip_address, url_start, ip_address)
    results_waf = subprocess.check_output(WAFSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with WAF-scan for " + ip_address + bcolors.ENDC
    print results_waf
    write_to_file(ip_address, "waf", results_waf)
    return

def wafssl(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting firewall scan for " + ip_address + bcolors.ENDC
    WAFSSLSCAN = "wafw00f %s://%s:%s -a | tee -a %s%s/webapp_scans/waf-%s.txt" % (url_start, ip_address, port, dirs, ip_address, ip_address)
    #WIGSCAN = "wig-git -t 20 -l %s%s/webapp_scans/http-dirb-%s.txt --no_cache_load --no_cache_save -w %s%s/webapp_scans/%s-wig-%s.txt | sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g'" % (dirs, ip_address, ip_address, dirs, ip_address, url_start, ip_address)
    results_wafssl = subprocess.check_output(WAFSSLSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with WAFSSL-scan for " + ip_address + bcolors.ENDC
    print results_wafssl
    write_to_file(ip_address, "wafssl", results_wafssl)
    return

def nikto(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting nikto scan for " + ip_address + bcolors.ENDC
    NIKTOSCAN = "nikto -maxtime 5m -h %s://%s:%s | tee -a %s%s/webapp_scans/nikto-%s-%s.txt" % (url_start, ip_address, port, dirs, ip_address, url_start, ip_address)
    print bcolors.HEADER + NIKTOSCAN + bcolors.ENDC
    results_nikto = subprocess.check_output(NIKTOSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with NIKTO-scan for " + ip_address + bcolors.ENDC
    print results_nikto
    write_to_file(ip_address, "nikto", results_nikto)
    return

def ssl(ip_address, port, url_start):
    print bcolors.HEADER + "INFO: Starting ssl scan for " + ip_address + bcolors.ENDC
    SSLSCAN = "sslscan %s:%s |  sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g' |  tee %s%s/webapp_scans/ssl_scan_%s" % (ip_address, port, dirs, ip_address, ip_address)
    print bcolors.HEADER + SSLSCAN + bcolors.ENDC
    results_ssl = subprocess.check_output(SSLSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with SSL-scan for " + ip_address + bcolors.ENDC
    print results_ssl
    write_to_file(ip_address, "ssl-scan", results_ssl)
    return

def httpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected http on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing web app based scans for " + ip_address + ":" + port + bcolors.ENDC
    nikto_process = multiprocessing.Process(target=nikto, args=(ip_address,port,"http"))
    nikto_process.start()
    parsero_process = multiprocessing.Process(target=parsero, args=(ip_address,port,"http"))
    parsero_process.start()
    wig_process = multiprocessing.Process(target=wig, args=(ip_address,port,"http"))
    wig_process.start()
    waf_process = multiprocessing.Process(target=waf, args=(ip_address,port,"http"))
    waf_process.start()
    print bcolors.HEADER + "INFO: Checking for response on port " + port + bcolors.ENDC
    url = "http://"+ip_address+":"+port+"/xxxxxxx"
    response = requests.get(url)
    print ""
    print response
    if response.status_code == 404: #could also check == requests.codes.ok
        print bcolors.HEADER + "INFO: Response was 404 on port "+port+", perfoming directory scans" + bcolors.ENDC
        dirb_process = multiprocessing.Process(target=dirb, args=(ip_address,port,"http"))	
        dirb_process.start()
    else:
        print bcolors.HEADER + "INFO: Response was not 404 on port "+port+", skipping directory scans" + bcolors.ENDC
    print ""
    return

def httpsEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected https on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing web app based scans for " + ip_address + ":" + port + bcolors.ENDC
    nikto_process = multiprocessing.Process(target=nikto, args=(ip_address,port,"https"))
    nikto_process.start()
    parsero_process = multiprocessing.Process(target=parsero, args=(ip_address,port,"https"))
    parsero_process.start()
    ssl_process = multiprocessing.Process(target=ssl, args=(ip_address,port,"https"))
    ssl_process.start()
    wig_process = multiprocessing.Process(target=wigssl, args=(ip_address,port,"https"))
    wig_process.start()
    waf_process = multiprocessing.Process(target=wafssl, args=(ip_address,port,"https"))
    waf_process.start()
    print ""
    print bcolors.HEADER + "INFO: Checking for response on port " + port + bcolors.ENDC
    url = "https://"+ip_address+":"+port+"/xxxxxxx"
    response = requests.get(url)
    print response
    if response.status_code == 404: #could also check == requests.codes.ok
        print bcolors.HEADER + "INFO: Response was 404 on port "+port+", perfoming directory scans" + bcolors.ENDC
        dirb_ssl_process = multiprocessing.Process(target=dirbssl, args=(ip_address,port,"https"))	
        dirb_ssl_process.start()
    else:
        print bcolors.HEADER + "INFO: Response was not 404 on port "+port+", skipping directory scans" + bcolors.ENDC
    print ""
    return

def mssqlEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected MS-SQL on " + ip_address + ":" + port + bcolors.ENDC
    print bcolors.HEADER + "INFO: Performing nmap mssql script scan for " + ip_address + ":" + port + bcolors.ENDC
    MSSQLSCAN = "nmap -sV -Pn -p %s --script=ms-sql-info,ms-sql-config,ms-sql-dump-hashes --script-args=mssql.instance-port=1433,smsql.username-sa,mssql.password-sa -oN %s%s/service_scans/mssql_%s.nmap %s" % (port, dirs, ip_address, ip_address, ip_address)
    print bcolors.HEADER + MSSQLSCAN + bcolors.ENDC
    mssql_results = subprocess.check_output(MSSQLSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with MSSQL-scan for " + ip_address + bcolors.ENDC
    print mssql_results
    return

def smtpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected smtp on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "smtp")
    SMTPSCAN = "nmap -sV -Pn -p %s --script=smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-cve2011-1764 %s -oN %s%s/service_scans/smtp_%s.nmap" % (port, ip_address, dirs, ip_address, ip_address)
    print bcolors.HEADER + SMTPSCAN + bcolors.ENDC
    smtp_results = subprocess.check_output(SMTPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with SMTP-scan for " + ip_address + bcolors.ENDC
    print smtp_results
    write_to_file(ip_address, "smtp-connect", smtp_results)
    return
    
def smbEnum(ip_address, port):
    print "INFO: Detected SMB on " + ip_address + ":" + port
    print bcolors.HEADER + "INFO: Performing SMB based scans for " + ip_address + ":" + port + bcolors.ENDC
    SMBMAP = "smbmap -H %s | tee %s%s/service_scans/smbmap_%s" % (ip_address, dirs, ip_address, ip_address)
    smbmap_results = subprocess.check_output(SMBMAP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with SMBMap-scan for " + ip_address + bcolors.ENDC
    print smbmap_results
    write_to_file(ip_address, "smbmap", smbmap_results)
    return

def rpcEnum(ip_address, port): 
    print bcolors.HEADER + "INFO: Detected RPC on " + ip_address + ":" + port  + bcolors.ENDC
    RPCMAP = "impacket-rpcdump %s  | tee %s%s/service_scans/rpcmap_%s" % (ip_address, dirs, ip_address, ip_address)
    rpcmap_results = subprocess.check_output(RPCMAP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with RPC-scan for " + ip_address + bcolors.ENDC
    print rpcmap_results
    write_to_file(ip_address, "rpcmap", rpcmap_results)
    return

def samrEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected SAMR on " + ip_address + ":" + port  + bcolors.ENDC
    SAMRDUMP = "impacket-samrdump %s | tee %s%s/service_scans/samrdump_%s" % (ip_address, dirs, ip_address, ip_address)
    samrdump_results = subprocess.check_output(SAMRDUMP, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with SAMR-scan for " + ip_address + bcolors.ENDC
    print samrdump_results
    write_to_file(ip_address, "samrdump", samrdump_results)
    return

def ftpEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected ftp on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "ftp")
    FTPSCAN = "nmap -sV -Pn -vv -p %s --script=ftp-anon,ftp-bounce,ftp-libopie,ftp-proftpd-backdoor,ftp-vsftpd-backdoor,ftp-vuln-cve2010-4221 -oN %s%s/service_scans/ftp_%s.nmap %s" % (port, dirs, ip_address, ip_address, ip_address)
    print bcolors.HEADER + FTPSCAN + bcolors.ENDC
    results_ftp = subprocess.check_output(FTPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with FTP-Nmap-scan for " + ip_address + bcolors.ENDC
    print results_ftp
    return

def nfsEnum(ip_address, port):
    print bcolors.HEADER + "INFO: Detected NFS on " + ip_address + bcolors.ENDC
    SHOWMOUNT = "showmount -e %s | tee %s%s/service_scans/nfs_%s.nmap"  % (ip_address, dirs, ip_address, ip_address)
    print bcolors.HEADER + SHOWMOUNT + bcolors.ENDC
    nfsscan_results = subprocess.check_output(SHOWMOUNT, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with NFS-scan for " + ip_address + bcolors.ENDC
    print nfsscan_results
    write_to_file(ip_address, "nfsscan", nfsscan_results)
    return

def sshScan(ip_address, port):
    print bcolors.HEADER + "INFO: Detected SSH on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "ssh")
    ssh_process = multiprocessing.Process(target=sshBrute, args=(ip_address,port))
    ssh_process.start()
    return

def sshBrute(ip_address, port):    
    print bcolors.HEADER + "INFO: SSH Bruteforce on " + ip_address + ":" + port  + bcolors.ENDC
    SSHSCAN = "hydra -I -C /opt/doubletap-git/wordlists/quick_hit.txt  -t 3 ssh://%s -s %s | grep target" % (ip_address, port)
    results_ssh = subprocess.check_call(SSHSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with SSH-Bruteforce check for " + ip_address + bcolors.ENDC
    #print results_ssh
    write_to_file(ip_address, "sshscan", results_ssh)
    return

def pop3Scan(ip_address, port):
    print bcolors.HEADER + "INFO: Detected POP3 on " + ip_address + ":" + port  + bcolors.ENDC
    connect_to_port(ip_address, port, "pop3")

def vulnEnum(ip_address):
    print bcolors.OKGREEN + "INFO: Running Vulnerability based nmap scans for " + ip_address + bcolors.ENDC
    VULN = "nmap -sV --script=vuln --script-timeout=600 %s -oN %s%s/port_scans/vuln_%s.nmap" % (ip_address, dirs, ip_address, ip_address)
    #VULN = "nmap -sV -p%s --script=vuln --script-timeout=300 %s -oN %s%s/port_scans/vuln_%s.nmap" % (port_list, ip_address, dirs, ip_address, ip_address)
    vuln_results = subprocess.check_output(VULN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with VULN-scan for " + ip_address + bcolors.ENDC
    print vuln_results
    write_to_file(ip_address, "vulnscan", vuln_results)
    return

def udpScan(ip_address):
    print bcolors.OKGREEN + "INFO: Running UDP nmap scan on " + ip_address + bcolors.ENDC
    UDPSCAN = "nmap -Pn -A -sC -sU -T 4 --top-ports 200 -oN %s%s/port_scans/udp_%s.nmap %s"  % (dirs, ip_address, ip_address, ip_address)
    #print bcolors.HEADER + UDPSCAN + bcolors.ENDC
    udpscan_results = subprocess.check_output(UDPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: CHECKFILE - Finished with UDP-Nmap scan for " + ip_address + bcolors.ENDC
    print udpscan_results
    write_to_file(ip_address, "udpscan", udpscan_results)
    #UNICORNSCAN = "unicornscan -mU -v -I %s > %s%s/port_scans/unicorn_udp_%s.txt" % (ip_address, dirs, ip_address, ip_address)
    #unicornscan_results = subprocess.check_output(UNICORNSCAN, shell=True)
    #print bcolors.OKGREEN + "INFO: RESULTS BELOW - Finished with UNICORN-UDP-scan for " + ip_address + bcolors.ENDC
    #print unicornscan_results
    return

def tcpScan(ip_address):
    print bcolors.OKGREEN + "INFO: Running Full TCP nmap scan on " + ip_address  + bcolors.ENDC
    #TCPALL = "unicornscan -p a %s | tee %s%s/port_scans/fulltcp_%s.nmap" % (ip_address, dirs, ip_address, ip_address)
    TCPALL = "nmap -sV -Pn -p1-65535 --max-retries 1 --max-scan-delay 10 --defeat-rst-ratelimit --open -T4 %s | tee %s%s/port_scans/fulltcp_%s.nmap" % (ip_address, dirs, ip_address, ip_address)
    tcp_results = subprocess.check_output(TCPALL, shell=True, stderr=None)
    print bcolors.OKGREEN + "INFO: CHECK FILE - Finished with FULL-TCP-scan for " + ip_address + bcolors.ENDC
    print tcp_results
    write_to_file(ip_address, "fulltcpscan", tcp_results)
    return

#Starting funtion to parse and pipe to multiprocessing
def nmapScan(ip_address):
    ip_address = ip_address.strip()
    print ""
    print bcolors.OKGREEN + "INFO: Current default output directory set as " + bcolors.ENDC + dirs
    print bcolors.OKGREEN + "INFO: Host IP set as " + bcolors.ENDC + myip
    print ""
    #print bcolors.OKGREEN + "INFO: Running general TCP Unicorn scan for " + ip_address + bcolors.ENDC
    #PORTSCAN = "unicornscan %s "  % (ip_address)
    #print bcolors.HEADER + PORTSCAN + bcolors.ENDC
    #open_ports = subprocess.check_output(PORTSCAN, shell=True)
    #if not open_ports:
    #    print bcolors.FAIL + "INFO: There are no open common ports for " + ip_address + bcolors.ENDC
    #    print bcolors.OKGREEN + "INFO: Running full TCP Unicorn scan for " + ip_address + " this may take a while..." + bcolors.ENDC
    #    PORTSCAN = "unicornscan -p a %s "  % (ip_address)
    #    print bcolors.HEADER + PORTSCAN + bcolors.ENDC
    #    open_ports = subprocess.check_output(PORTSCAN, shell=True)
    #    if not open_ports:
    #        print bcolors.FAIL + "FAIL: There are no open ports for " + ip_address + bcolors.ENDC
    #        return
    #    return
    #print open_ports
    #ports_dirty= ",".join(re.findall('\[(.*?)\]', open_ports))
    #port_list = ports_dirty.replace(' ', '')
    m = multiprocessing.Process(target=tcpScan, args=(scanip,))
    m.start()
    n = multiprocessing.Process(target=udpScan, args=(scanip,))
    n.start()
    l = multiprocessing.Process(target=vulnEnum, args=(scanip,))
    l.start()
    print bcolors.OKGREEN + "INFO: Running General TCP nmap scans for " + ip_address + bcolors.ENDC
    #TCPSCAN = "nmap -sV -O -p%s %s -oN %s%s/%s.nmap"  % (port_list, ip_address, dirs, ip_address, ip_address)
    TCPSCAN = "nmap -sV -Pn -O %s -oN %s%s/port_scans/%s.nmap"  % (ip_address, dirs, ip_address, ip_address)
    #print bcolors.HEADER + TCPSCAN + bcolors.ENDC
    results = subprocess.check_output(TCPSCAN, shell=True)
    print bcolors.OKGREEN + "INFO: RESULT BELOW - Finished with BASIC Nmap-scan for " + ip_address + bcolors.ENDC
    print results
#    write_to_file(ip_address, "portscan", results)
    lines = results.split("\n")
    serv_dict = {}
    for line in lines:
        ports = []
        line = line.strip()
        if ("tcp" in line) and ("open" in line) and not ("Discovered" in line):
            # print line
            while "  " in line:
                line = line.replace("  ", " ");
            linesplit= line.split(" ")
            service = linesplit[2] # grab the service name

            port = line.split(" ")[0] # grab the port/proto
            # print port
            if service in serv_dict:
                ports = serv_dict[service] # if the service is already in the dict, grab the port list

            ports.append(port)
            # print ports
            serv_dict[service] = ports # add service to the dictionary along with the associated port(2)
            print ports



   #Search through the service dictionary to call additional targeted enumeration functions
    for serv in serv_dict:
        ports = serv_dict[serv]
        if (serv == "http") or (serv == "http-proxy") or (serv == "http-alt") or (serv == "http?") or (serv == "http-proxy?"):
            for port in ports:
                port = port.split("/")[0]
                multProc(httpEnum, ip_address, port)
        elif (serv == "ssl/http") or ("https" == serv) or ("https?" == serv):
            for port in ports:
                port = port.split("/")[0]
                multProc(httpsEnum, ip_address, port)
        elif "smtp" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(smtpEnum, ip_address, port)
        elif "ftp" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(ftpEnum, ip_address, port)
        elif ("microsoft-ds" in serv) or ("netbios-ssn" == serv):
            for port in ports:
                port = port.split("/")[0]
                multProc(smbEnum, ip_address, port)
                multProc(rpcEnum, ip_address, port)
                multProc(samrEnum, ip_address, port)
        elif "ms-sql" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(mssqlEnum, ip_address, port)
        elif "rpcbind" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(nfsEnum, ip_address, port)
        elif "ssh" in serv:
            for port in ports:
                port = port.split("/")[0]
                multProc(sshScan, ip_address, port)
   
    return

#PSA's
print bcolors.HEADER
print "------------------------------------------------------------"
print "!!!!                     DOUBLETAP                     !!!!!"
print "!!!!                A script kiddies delite            !!!!!"
print "!!!!  An all in one recon and target template creator  !!!!!"
print "!!!!            Automagically runs the following       !!!!!"
print "!!!!     gobuster, nikto, ftp, ssh, mssql, pop3, tcp   !!!!!"
print "!!!!           udp, smtp, smb, wig, hydra              !!!!!"
print "------------------------------------------------------------"



if len(sys.argv) < 2:
    print ""
    print "Usage: python doubletap.py <ip> <ip> <ip>"
    print "Example: python doubletap.py 192.168.1.101 192.168.1.102"
    print "Current default output directory set as " + dirs
    print "Host IP set as " + myip
    print ""
    print "############################################################"
    pass
    sys.exit()

print bcolors.ENDC

#Main start and folder creation
if __name__=='__main__':

    # Setting ip targets
    targets = sys.argv
    targets.pop(0)

    for scanip in targets:
        scanip = scanip.rstrip()
        if not scanip in subprocess.check_output("ls " + dirs, shell=True):                   
            print bcolors.HEADER + "INFO: No folder was found for " + scanip + ". Setting up folder." + bcolors.ENDC
            subprocess.check_output("mkdir " + dirs + scanip, shell=True)
            subprocess.check_output("mkdir " + dirs + scanip + "/exploits", shell=True)
            subprocess.check_output("mkdir " + dirs + scanip + "/privesc", shell=True)
            subprocess.check_output("mkdir " + dirs + scanip + "/service_scans", shell=True)
            subprocess.check_output("mkdir " + dirs + scanip + "/webapp_scans", shell=True)
            subprocess.check_output("mkdir " + dirs + scanip + "/port_scans", shell=True)
            print bcolors.OKGREEN + "INFO: Folder created here: " + dirs + scanip + bcolors.ENDC
            subprocess.check_output("cp /opt/doubletap-git/templates/windows-template.md " + dirs + scanip + "/" + scanip + "-windows-exploit-steps.md", shell=True)
            subprocess.check_output("cp /opt/doubletap-git/templates/linux-template.md " + dirs + scanip +  "/" + scanip + "-linux-exploit-steps.md", shell=True)
            subprocess.check_output("cp /opt/doubletap-git/templates/windows-worksheet-template.md " + dirs + scanip + "/" + scanip + "-windows-notes.md", shell=True)
            subprocess.check_output("cp /opt/doubletap-git/templates/linux-worksheet-template.md " + dirs + scanip + "/" + scanip + "-linux-notes.md", shell=True)
            print bcolors.OKGREEN + "INFO: Added pentesting templates: " +  dirs + scanip + bcolors.ENDC
            subprocess.check_output("sed -i -e 's/INSERTIPADDRESS/" + scanip + "/g' " + dirs + scanip + "/" + scanip + "-windows-exploit-steps.md", shell=True)
            subprocess.check_output("sed -i -e 's/MYIPADDRESS/" + myip + "/g' " + dirs + scanip + "/" + scanip + "-windows-exploit-steps.md", shell=True)
            subprocess.check_output("sed -i -e 's/INSERTIPADDRESS/" + scanip + "/g' " + dirs + scanip + "/" + scanip + "-linux-exploit-steps.md", shell=True)
            subprocess.check_output("sed -i -e 's/MYIPADDRESS/" + myip + "/g' " + dirs + scanip + "/" + scanip + "-linux-exploit-steps.md", shell=True)
           

        p = multiprocessing.Process(target=nmapScan, args=(scanip,))
        time.sleep(1) #Just a nice wait for unicornscan 
        p.start()
        
