#!/usr/bin/env python
"""
# ****************************************************************************
# Ericsson Radio Systems AB                                     SCRIPT
# ****************************************************************************
#
#
# (c) Ericsson Radio Systems AB 2021 - All rights reserved.
#
# The copyright to the computer program(s) herein is the property
# of Ericsson Radio Systems AB, Sweden. The programs may be used
# and/or copied only with the written permission from Ericsson Radio
# Systems AB or in accordance with the terms and conditions stipulated
# in the agreement/contract under which the program(s) have been
# supplied.
#
# ******************************************************************************
# Name				: ProCus_tp_packaging_script.py
# Devloper			: Shashi Kumar V (XKUSHAS)
# Date of creation	: 03/16/2021
# Purpose			: To pull required packages from NEXUS and to create a zip file
#
#
# ******************************************************************************
"""
import re
import os
import sys
import shutil
import base64
import datetime
import fileinput
import urllib.request
import urllib.request as ur
from shutil import copyfile
main_url = 'https://arm1s11-eiffel013.eiffel.gic.ericsson.se:8443/nexus/content/repositories/eniq_procus/ENIQ_ProCus_TP/'
std_parser_url = 'https://arm1s11-eiffel013.eiffel.gic.ericsson.se:8443/nexus/content/repositories/eniq_platform/Packages/'
procus_parser_url = 'https://arm1s11-eiffel013.eiffel.gic.ericsson.se:8443/nexus/content/repositories/eniq_platform/Procus/'
package_list_order = ['DIM_E','DC_','INTF_DIM','INTF_DC']
list_to_remove_TP_list4=['LOGS','PACKAGES','3GPP32435DYN_OCC_R6E02b3.zip','build.properties','update_feature_list.sh','create_packagelist.pl','tpiUnwrapper.jar','FD/','Model-T/','eascii_R13C02b75.zip','parser.txt','3GPP32435DYN_R13H03_EC01b133.zip','Xml3gpp32435eceParser_5-0-0_b3.zip','export_R11E02_EC02b288.zip','repository_R15D03_EC07b1805.zip']
package_list = []
my_readme_list = ['$Current_year$','$TP_name$','$TP_zip_name$','$Creation_Date$','$TR_name$','$DIM_E_CN_depend$','$TP_product_number$','$Eridoc_revision$','$Parser$','$cp_parser$','$install_parser$','$Interface_activation$','$Universe$','$Universe_zip_name$','$Tech_Pack_User_Guide_name$','$Tech_Pack_User_Guide_number$']
my_readme_list1 = []
readme_interfaces_list = []
Universe_zip_name = []
readme_interfaces_string = "# cd /eniq/sw/installer"
man_readme_interfaces_string = "# cd /eniq/sw/installer"
readme_dict = {}

# Variables define to be used for readme creation
temp_cp_parser = """	# cp /var/tmp/ENIQ_PC_upgrade/$Parser_name$ /eniq/sw/installer/\n"""
cp_parser = ""
temp_install_parser = """	# ./platform_installer """
install_parser = ""
Parser_string = """
3.1.1 Copy the parser(s) from folder /var/tmp/ENIQ_PC_upgrade
	  to /eniq/sw/installer as dcuser
$cp_parser$
3.1.2 install the parser as dcuser
	# cd /eniq/sw/installer
$install_parser$
3.1.3 Restart the engine
    # engine restart"""
Universe_zip_name_temp = ""
Universe_string = """*(In case of MultiBlade, Run this below step on Coordinator blade)*
5.1	Switch user to dcuser
	# su - dcuser

5.2	Create directory for the BO package
	# cd /eniq/sw/installer
	# [ ! -d BO_tmp ] && mkdir BO_tmp
	# [ ! -d bouniverses ] && mkdir bouniverses

5.3	copy the BO tech pack tpi(s) file to the BO folder created
$Universe_zip_name$
5.4	run extract report packages script
	# cd /eniq/sw/installer
	# ./extract_report_packages.bsh /eniq/sw/installer/BO_tmp /eniq/sw/installer/bouniverses

5.5	Exit from dcuser
	# exit

5.6	Follow the Ericsson Business Intelligence Deployment Installation and Upgrade
	Instructions to install the universes
	(1/1531-CNA4031452 LATEST Section "ENIQ Universes and Reports")."""

###########################################################################################################################################
# Function to clear the temp readme folder
def clean_up_readme_folder():
	if 'temp' in os.listdir('h:\\packaging\\readme'):
		os.chdir('h:\\packaging\\readme\\temp')
		os.system('rm -rf *')
	else:
		print ("It's not there")
		os.chdir('h:\\packaging\\readme')
		os.system('mkdir temp')

# Initial function to selct the TP which has to be packaged
def TP_selection_prompt():	
	TP_list1 = []
	s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + main_url).read()
	s1 = str(s)
	
	for x in re.findall('''.*\">(.+)</a></td>.*''', s1):
#		print (x)
		TP_list1.append(x)
	
	TP_list1 = [w.replace('/', '') for w in TP_list1]
	
	print("Please enter the TP name you want to package: Ex: CS or DMF\n")
	TP_list1.remove('Parent Directory') # Removing the parent directory
	
	for i in TP_list1[0:5]:	
		print ('* '+i)
	
	while True:	
		try:
			global TP_sel_input
			TP_sel_input = input()
			TP_sel_input=TP_sel_input.upper()
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
			
		if TP_sel_input in TP_list1:
			print ('')
			print ('The selected TP is ' + TP_sel_input)
			print ('')
			break
		else:
			print('Invalid Input')
			continue

# Function to display contents from the selcted TP
def lst_in_selected_tp():
	global TP_list4
	#####To get the contents from web - third one
	# Calling the URL
	s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + main_url+'/'+TP_sel_input+'/').read()
	sl = str(s)
	
	# Finding and matching only the folder structure
	for a in re.findall('''.*">(.+)</a></td>.*''', sl):
		TP_list3.append(a)
	if 'Parent Directory' in TP_list3:
		TP_list3.remove('Parent Directory')
	else:
		pass
	if 'PACKAGES/' in TP_list3:
		TP_list3.remove('PACKAGES/')
	else:
		pass
	if 'LOGS/' in TP_list3:
		TP_list3.remove('LOGS/')
	else:
		pass
	TP_list4=TP_list3
	for z in list_to_remove_TP_list4:
		if z in TP_list4:TP_list4.remove(z)
# Packagelist file creation
def package_list_creation():
	global readme_interfaces_list
	with open('packagelist.txt', 'w') as g:
		for h in package_list_order:
			for i in package_list:
				if i.startswith(h):
					g.write(i+'\n')
					if i.startswith('INTF_DIM') or i.startswith('INTF_DC'):
						if i not in readme_interfaces_list:
							readme_interfaces_list.append("%s" % i)
						else:
							pass
					else:
						pass
	g.close()
	os.system('dos2unix packagelist.txt')# To remove ^M/extra unwanted characters from the file|To convert data inside file into Bytecode

# Function to get latest file name from the folders available in the selected Tech Pack folder
def all_latest():
	for a in TP_list4:
		s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + main_url+'/'+TP_sel_input+'/'+a).read()
		sl = str(s)
		
		# Finding and matching only the folder structure
		for b in re.findall('''.*">(.+)</a></td>.*''', sl):
			TP_list5.append(b)
			if 'Parent Directory' in TP_list5:TP_list5.remove('Parent Directory') #To remove parent directory
		TP_list5.sort()
		TP_all_latest.append(TP_list5[-1])# Latest file without link		
		all_latest_download.append(main_url+TP_sel_input+'/'+a+TP_list5[-1])# The latest files name with link
		TP_list5.clear()

# Listing/displaying the selected package name
def dislp_sel_pkg(x):
	print ('Selected the below packages')
	global package_list
	global Universe_zip_name
	for a in x:
		for b in re.findall('(.*)_.*_.*', a):
			package_list.append(b)
		if a.startswith('BO_E'):
			Universe_zip_name.append(a)
	x.append('update_feature_list.sh')
	
	for (i, item) in enumerate(x, start=1):
		print(i,item,sep=' - ')

# Clean-up of temp folder
def clean_up():
	if 'temp' in os.listdir('h:\\packaging'):
		os.chdir('h:\\packaging\\temp')
		os.system('rm -rf *')
	else:
		print ("It's not there")
		os.system('mkdir temp')

# Function to take parser hyperlink as input
def parser_hyperlink():
	global sel_parser1
	global parser_name
	global parser_to_be_included
	while True:		
		try:
			parser_link = input('Please provide the hyperlink : ')
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if parser_link[:8] == 'https://' and parser_link[-4:] == '.zip':
			os.chdir('h:\\packaging\\temp')
			try: ######################################### Have to handle
				os.system('curl -# -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")+ '" -O ' + parser_link)
				temp_parser_name = re.findall('''.*/(.+)''',parser_link)
				parser_name = str(temp_parser_name[0])
				sel_parser1.append(str(temp_parser_name[0]))
				print ('\nDo you want to include one more parser?')
				yes_no('\nPrompt for the next parser\n', '\nNo more parser to include',parser_type_input)
				parser_to_be_included = 'yes'
			except pycurl.error:
				print ('Print could not download the parser, please contact the developer') ######################################### Have to handle
			break
		elif parser_link in ['NO','no','No']:
			break
		else:
			print ("The link doesn't seem like an hyperlink")
			continue

# Function for providing parser name
parser_name = ''
parser_to_be_included = ''
def parser_input(x):
	global sel_parser
	global sel_parser1
	global parser_name
	global parser_to_be_included
	sel_parser = []
	while True:
		try:
			parser_prompt = input('\nPlease provide the parser name : ')
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if parser_prompt is not None and parser_prompt[-4:] == '.zip':
			s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + x).read()
			sl = str(s)
			
			for a in re.findall('''.*">(.+)</a></td>.*''', sl):
				if a != 'Parent Directory':				
					s2 = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + x + a).read()
					s3 = str(s2)
					
					for b in re.findall('''.*">(.+)</a></td>.*''', s3):
						if parser_prompt == b:
							parser_name = b
							print('\nParser build found')
							sel_parser.append(x+a+b)
							temp_parser_verify=b
							parser_to_be_included = 'yes'
				else:
					pass
			if sel_parser == []:
				print ("\ncouldn't find the parser")
				print ("Do you want to provide parser details again?")
				yes_no('\nPlease provide the parser name to include\n', '\nNo more parser to include',parser_type_input)
			elif temp_parser_verify in sel_parser1:
				print ("\nSame parser name provided again\n")
				print ("Do you want to provide parser details again?")
				yes_no('\nPlease provide the parser name to include\n', '\nNo more parser to include',parser_type_input)
			elif len(sel_parser) == 1:
				sel_parser1.append(temp_parser_verify)
				print ('\nDownloading parser package, please wait......')
				os.chdir('h:\\packaging\\temp')
				os.system('curl -# -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")+ '" -O ' + sel_parser[0])
				print ('\nDo you want to include one more parser?')
				yes_no('\nPrompt for the next parser\n', '\nNo more parser to include',parser_type_input)
			break
		else:
			print ('Invalid input')
			continue

# Prompt to select the input method for providign parser name			
def parser_or_hyperlink(y):
	print ('Please select one of the below input method to provide parser input')
	print ('NOTE : I would prefer Hyperlink as it would take less prcessing time and can be quick!!!')
	for (i, items) in enumerate(['Parser_name','Hyperlink','skip_parser'], start=1):
		print(i, items, sep=') ')
	while True:		
		try:
			parser_or_link = input('Please choose 1 or 2 : ')
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if parser_or_link == 'Parser_name' or parser_or_link == '1':
			parser_input(y)
			break
		elif parser_or_link == 'Hyperlink' or parser_or_link == '2':
			parser_hyperlink()
			break
		elif parser_or_link == 'skip_parser' or parser_or_link == '3':
			break
		else:
			print ("Invalid input")
			continue

# Prompt to select the parser path based on the team parser belongs to
def parser_type_input():
	print ('The parser to be included is Standard or Procus parser?')
	parser_type = ["Standard_parser", "ProCus_parser","skip_parser"]# Dummy list for list types
	for (i, item) in enumerate(parser_type, start=1):
		print(i,item,sep=' - ')
	while True:
		try:
			parser_type_prompt = input('Please select on of the two options : ')
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if parser_type_prompt == "Standard_parser" or parser_type_prompt == '1':
			print ("\nThe selected parser type is Standard parser\n")
			main_parser_url = std_parser_url
			parser_or_hyperlink(main_parser_url)
			break
		elif parser_type_prompt == "ProCus_parser" or parser_type_prompt == '2':
			print ("The selected parser type is ProCus parser\n")
			main_parser_url = procus_parser_url
			parser_or_hyperlink(main_parser_url)
			break
		elif parser_type_prompt == "skip_parser" or parser_type_prompt == '3':
			break
		else:
			print ('Invalid input')
			continue

# Readme to be created or not
def readme_creation_prompt():
	global readme_input
	print ('Do you want to create readme for Linux track or Solaris?')
	for (i, items) in enumerate(['Linux', 'Solaris'], start=1):
		print (i, items, sep=') ')
	while True:
		try:
			readme_input = input("Please specify 1 or 2 : ")
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
	
		if str(readme_input) == '1':
			readme_path = 'h:\\packaging\\readme\\Linux\\'
			print ('Readme path is '+readme_path)
			readme_creation_input()
			break
		elif str(readme_input) == '2':
			readme_path = 'h:\\packaging\\readme\\Linux\\'
			print ('Readme path is '+readme_path)
			readme_creation_input()
			break
		else:
			print ('Invalid input')
			continue			

# Generic Yes or No prompt
def yes_no(a, b, c):
	while True:
		try:
			simple_prompt = input("Please specify yes or no : ")
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if simple_prompt in ['YES','yes','Yes']:
			print (a)
			c()
			break
		elif simple_prompt in ['NO','no','No']:
			print (b)
			if arg1 == '-t':
				exit()
			break
		else:
			print ('Invalid input')
			continue

# Function to download the selected packages
def all_latest_pkg_download():
	if pkg_type_input == 1:
		x = all_latest_download
	elif pkg_type_input == 2:
		x = all_manual_tp_download
	x.append(main_url+'/'+TP_sel_input+'/'+'update_feature_list.sh')
	print ('\nDownloading packages please wait....')
	os.chdir('h:\\packaging\\temp')
	if len(package_list) == 1 and package_list[0].startswith('BO_E'):
		pass		
	else:
		package_list_creation()
	for a in x:
		os.system('curl -# -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")+ '" -O '  + a)
	print ('')
	print ('Downloaded the selected packages......\n')
	print ('Do you want to include one more TP?')
	yes_no('\nOne more tp to be included....\n', '\nno other tp to include\n', temp_prompt1)

# To zip the downloaded files
def pkg_zip():
	os.chdir('h:\\packaging')
	shutil.make_archive('ENIQ_'+TP_sel_input, 'zip', 'temp')
	print ("\nENIQ_"+TP_sel_input+".zip "+"Package created under 'h\packaging' folder\n")

# Prompt to download the selected packages
def pkg_conf_prompt(f):	
	print ("\nDo you want to download the below packages?")
	while True:
		try:
			global pkg_conf_input
			pkg_conf_input = input("""Please specify 'Yes' or 'No' : """)
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
	
		if str(pkg_conf_input) in ['YES','yes','Yes']:
			f()
			break
		elif str(pkg_conf_input) in ['NO','no','No']:
			print('Exiting script......')
			exit()
		else:
			print ('Invalid input')
			continue

# Function to select the tpi files manually
def manual_tp_list():
	global TP_list6
	for a in TP_list4:	
		s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + main_url+'/'+TP_sel_input+'/'+a).read()
		sl = str(s)
		
		# Finding and matching only the folder structure
		for b in re.findall('''.*">(.+)</a></td>.*''', sl):
			TP_list6.append(b)
			if 'Parent Directory' in TP_list6:TP_list6.remove('Parent Directory') #To remove parent directory
		TP_list6.sort(reverse=True)
		TP_list6.insert(0, 'skip this file')
		len_TP_list6=len(TP_list6)
		TP_list6=TP_list6[0:6]
		print ('')
		print ('What '+a+' file you want to include in package?')
		for (i, item) in enumerate(TP_list6, start=0):
			print(i,item,sep=') ')
		def manual_tp_selection():
			man_tp_sel=input()
			try:
				if man_tp_sel == '0':
					return None
				elif man_tp_sel in TP_list6:
					TP_all_manual.append(man_tp_sel)
					all_manual_tp_download.append(main_url+'/'+TP_sel_input+'/'+a+man_tp_sel)
				elif int(man_tp_sel) in range (0,len_TP_list6+1):
					TP_all_manual.append(TP_list6[int(man_tp_sel)])
					all_manual_tp_download.append(main_url+'/'+TP_sel_input+'/'+a+TP_list6[int(man_tp_sel)])
				else:
					print('Invalid selection')
					return manual_tp_selection()
			except Exception as error:
				print ('Invalid selction')
				return manual_tp_selection()
		manual_tp_selection()			
		TP_list6.clear()

# Main function for readme creation where inputs are gathered
def readme_creation_input():
	for a in my_readme_list:
		if a == '$Current_year$':
			now = datetime.datetime.now()
			current_year = str(now.year)
			my_readme_list1.append(current_year)
			readme_dict[a] = current_year
		elif a == '$TP_zip_name$':
			if arg1 == '-r':
				man_TP_zip_name = input('Please provide input for '+a+' : ')
				my_readme_list1.append(man_TP_zip_name)
				readme_dict[a] = man_TP_zip_name
			else:
				my_readme_list1.append('ENIQ_'+TP_sel_input+'.zip')
				readme_dict[a] = 'ENIQ_'+TP_sel_input+'.zip'
		elif a == '$Creation_Date$':
			now = datetime.datetime.now()
			creation_date = str(str(now.day)+'/'+str(now.month)+'/'+str(now.year))
			my_readme_list1.append(creation_date)
			readme_dict[a] = creation_date
		elif a == '$TP_name$':
			global man_TP_name
			if arg1 == '-r':
				man_TP_name = input('Please provide input for '+a+' : ')
				my_readme_list1.append(man_TP_name)
				readme_dict[a] = man_TP_name
			else:
				my_readme_list1.append(TP_sel_input)
				readme_dict[a] = TP_sel_input
		elif a == '$TR_name$':
			TR_name = input('Please provide input for '+a+' : ')
			if TR_name == '':
				my_readme_list1.append('N/A')
				readme_dict[a] = 'N/A'
			else:
				my_readme_list1.append(TR_name)
				readme_dict[a] = TR_name
		elif a == '$DIM_E_CN_depend$':
			print ('Please provide input for '+a+' : ')
			while True:
				try:
					DIM_E_CN_depend = input("Please specify 'Yes' or 'No' : ")
				except ValueError:
					print("Sorry, I didn't understand that.")
					continue
			
				if str(DIM_E_CN_depend) in ['YES','yes','Yes']:
					my_readme_list1.append("""\nNote : There is a dependency on Ericsson Core Network Topology Tech Pack DIM_E_CN.
	   Ensure that the Topology Tech Pack is installed to allow correct functioning of this Tech Pack.""")
					readme_dict[a] = """\nNote : There is a dependency on Ericsson Core Network Topology Tech Pack DIM_E_CN.
	   Ensure that the Topology Tech Pack is installed to allow correct functioning of this Tech Pack."""
					break
				elif str(DIM_E_CN_depend) in ['NO','no','No']:
					my_readme_list1.append('')
					readme_dict[a] = ''
					break
				else:
					print ('Invalid input')
					continue
		elif a == '$TP_product_number$' and arg1 != '-r':
			test_input = input('Please provide input for '+a+' (Ex: CNA9032456, CNA8644126) : ')
			readme_dict[a] = test_input
		elif a == '$TP_product_number$' and arg1 == '-r':
			test_input = input('Please provide input for '+a+' (Ex: CNA9032456, CNA8644126) : ')
			my_readme_list1.append(test_input)
			readme_dict[a] = test_input
		elif a == '$Eridoc_revision$':
			test_input = input('Please provide input for '+a+' : ')
			my_readme_list1.append(test_input)
			readme_dict[a] = test_input
		elif a == '$Parser$' and arg1 != '-r':
			if parser_to_be_included == 'yes':# and len(sel_parser) == 1:
				my_readme_list1.append(Parser_string)
				readme_dict[a] = Parser_string
			else:
				my_readme_list1.append('No parser to install.')
				readme_dict[a] = 'No parser to install.'
		elif a == '$Parser$' and arg1 == '-r':
			print ('Do you want to include parser details?')
			global man_parser
			while True:
				try:
					man_parser = input("Please provide 'yes' or 'no' : ")
				except ValueError:
					print ('Invalid input')
					continue
				
				if str(man_parser) in ['YES','Yes','yes']:
					my_readme_list1.append(Parser_string)
					readme_dict[a] = Parser_string
					man_readme_parser_list = [item for item in input("Enter the parser name(s) with comma (,) seperation : ").split(',')]
					break
				elif str(man_parser) in ['NO','No','no']:
					my_readme_list1.append('No parser to install.')
					readme_dict[a] = 'No parser to install.'
					break
				else:
					print ('Invalid input')
					continue
		elif a == '$cp_parser$' and arg1 != '-r':
			global cp_parser
			for x in sel_parser1:
				cp_parser += temp_cp_parser.replace("$Parser_name$",x)
			readme_dict[a] = cp_parser
		elif a == '$install_parser$' and arg1 != '-r':
			global install_parser
			for x in sel_parser1:
				install_parser+=(temp_install_parser+str(x)+'\n')
			readme_dict[a] = install_parser
		elif a == '$cp_parser$' and arg1 == '-r' and str(man_parser) in ['YES','Yes','yes']:
			if 'No parser to install.' not in readme_dict.values():
				for x in man_readme_parser_list:
					cp_parser += temp_cp_parser.replace("$Parser_name$",x)
				readme_dict[a] = cp_parser
			else:
				pass
		elif a == '$install_parser$' and arg1 == '-r' and str(man_parser) in ['YES','Yes','yes']:
			if 'No parser to install.' not in readme_dict.values():
				for x in man_readme_parser_list:
					install_parser+=(temp_install_parser+str(x)+'\n')
				readme_dict[a] = install_parser
			else:
				pass
		elif a == '$Interface_activation$' and arg1 != '-r':
			global readme_interfaces_string
			if not readme_interfaces_list:
				my_readme_list1.append('No Interface to activate')
				readme_dict[a] = 'No Interface to activate'
			else:
				for x in readme_interfaces_list:
					readme_interfaces_string+=str("\n	# ./activate_interface -o <eniq_oss_name> -i "+x)
				my_readme_list1.append(readme_interfaces_string)
				readme_dict[a] = readme_interfaces_string
		elif a == '$Interface_activation$' and arg1 == '-r':
			global man_readme_interfaces_string
			print ('Do you want to include interface details in the readme?')
			while True:
				try:
					man_readme_interface_input = input('Please provide yes or no : ')
				except ValueError:
					print ('invalid input')
					continue
					
				if str(man_readme_interface_input) in ['YES','Yes','yes']:
					man_readme_interface_list = [item for item in input("Enter the interface list with comma (,) seperation : ").split(',')]
					for x in man_readme_interface_list:
						man_readme_interfaces_string+=str("\n	# ./activate_interface -o <eniq_oss_name> -i "+x)
					readme_dict[a] = man_readme_interfaces_string
					break
				elif str(man_readme_interface_input) in ['NO','No','no']:
					readme_dict[a] = "No Interface to activate"
					break
				else:
					print ('Invalid input')
					continue
		elif a == "$Universe$":
			if Universe_zip_name and arg1 != '-r':
				my_readme_list1.append(Universe_string)
				readme_dict[a] = Universe_string
			elif arg1 == '-r':
				global readme_universe_input
				print ('Do you want to include Universe details in the readme?')
				while True:
					try:
						readme_universe_input = input('Please provide yes or no : ')
					except ValueError:
						print ('Invalid input')
						continue
						
					if str(readme_universe_input) in ['YES','Yes','yes']:
						my_readme_list1.append(Universe_string)
						readme_dict[a] = Universe_string
						break
					elif str(readme_universe_input) in ['NO','No','no']:
						my_readme_list1.append("No Universe to decrypt")
						readme_dict[a] = "No Universe to decrypt"
						break
					else:
						print('Invalid input')
						continue
			else:
				my_readme_list1.append("No Universe to decrypt")
				readme_dict[a] = "No Universe to decrypt"
		elif a == '$Universe_zip_name$':
			global Universe_zip_name_temp
			if Universe_zip_name and arg1 != '-r':
				for x in Universe_zip_name:
					Universe_zip_name_temp+=("	# cp /var/tmp/ENIQ_PC_upgrade/"+str(x)+" /eniq/sw/installer/BO_tmp"+'\n')
				readme_dict[a] = Universe_zip_name_temp
			elif arg1 == '-r' and str(readme_universe_input) in ['YES','Yes','yes']:
				test_input = input('Please provide input for '+a+' : ')
				Universe_zip_name_temp+=("	# cp /var/tmp/ENIQ_PC_upgrade/"+str(test_input)+" /eniq/sw/installer/BO_tmp"+'\n')
				my_readme_list1.append(test_input)
				readme_dict[a] = Universe_zip_name_temp
		elif a == '$Tech_Pack_User_Guide_name$':
			TP_User_Guide_name = input('Please provide input for '+a+' : ')
			if TP_User_Guide_name == '':
				my_readme_list1.append('N/A')
				readme_dict[a] = 'N/A'
			else:
				my_readme_list1.append(TP_User_Guide_name)
				readme_dict[a] = TP_User_Guide_name
		elif a == '$Tech_Pack_User_Guide_number$':
			TP_User_Guide_number = input('Please provide input for '+a+' : ')
			if TP_User_Guide_name == '':
				my_readme_list1.append('N/A')
				readme_dict[a] = 'N/A'
			else:
				my_readme_list1.append(TP_User_Guide_number)
				readme_dict[a] = TP_User_Guide_number
	
	test_dict = dict(zip(my_readme_list, my_readme_list1))
	clean_up_readme_folder()
	
	if str(readme_input) == '1' and arg1 != '-r':
		copyfile('h:\\packaging\\readme\\Linux\\TP_readme_Linux.txt', 'h:\\packaging\\readme\\temp\\'+'ENIQ_'+TP_sel_input+'_readme.txt')
	elif str(readme_input) == '2' and arg1 != '-r':
		copyfile('h:\\packaging\\readme\\Solaris\\TP_readme_Solaris.txt', 'h:\\packaging\\readme\\temp\\'+'ENIQ_'+TP_sel_input+'_readme.txt')
	elif str(readme_input) == '1' and arg1 == '-r':
		copyfile('h:\\packaging\\readme\\Linux\\TP_readme_Linux.txt', 'h:\\packaging\\readme\\temp\\'+'ENIQ_'+man_TP_name+'_readme.txt')
	elif str(readme_input) == '2' and arg1 == '-r':
		copyfile('h:\\packaging\\readme\\Solaris\\TP_readme_Solaris.txt', 'h:\\packaging\\readme\\temp\\'+'ENIQ_'+man_TP_name+'_readme.txt')
		
	filelist = os.listdir('h:\\packaging\\readme\\temp')
	os.chdir('h:\\packaging\\readme\\temp')

	for line in fileinput.input(filelist, inplace=1):
		for key, value in readme_dict.items():
			if key in line:
				line = line.replace(key, value)
		sys.stdout.write(line)
		
	if arg1 == '-r':
		copyfile('h:\\packaging\\readme\\temp\\'+'ENIQ_'+man_TP_name+'_readme.txt', 'h:\\packaging\\'+'ENIQ_'+man_TP_name+'_readme.txt')
		print ("\n"+"ENIQ_"+man_TP_name+"_readme.txt"+" created under 'h\packaging' folder")
	else:
		copyfile('h:\\packaging\\readme\\temp\\'+'ENIQ_'+TP_sel_input+'_readme.txt', 'h:\\packaging\\'+'ENIQ_'+TP_sel_input+'_readme.txt')
		print ("\n"+"ENIQ_"+TP_sel_input+"_readme.txt"+" created under 'h\packaging' folder")
	clean_up_readme_folder()

# Function to decide the packaging type
def packaging_type_prompt(): # Third prompt to get the packaging type
	print ('Please selct what type of packaging you need: Ex: 1 or 2 or 3')
	packaging_type = ["All latest tpi's", "Manual selection of tpi's","Exit_script"]# Dummy list for list types
	for (i, item) in enumerate(packaging_type, start=1):
		print(i,item,sep=' - ')
	while True:
		try:
			global pkg_type_input
			pkg_type_input = input("""Please specify '1' or '2' : """)
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if pkg_type_input == '1':
			pkg_type_input = int(pkg_type_input)
			print ('')
			print ('The selected packaging type is ' + packaging_type[pkg_type_input-1])
			print ('')
			lst_in_selected_tp()
			all_latest()
			dislp_sel_pkg(TP_all_latest)
			pkg_conf_prompt(all_latest_pkg_download)
			print ('Do you want to include parser in the bundle?')
			yes_no('\nparser has to be included....\n', '\nno parser to include', parser_type_input)
			pkg_zip()
			print ('Do you want to create readme?')
			yes_no('\nReadme will be created\n', '\nReadme will not be created',readme_creation_prompt)
			break
		elif pkg_type_input == '2':
			pkg_type_input = int(pkg_type_input)
			print ('')
			print ('The selected packaging type is ' + packaging_type[pkg_type_input-1])
			lst_in_selected_tp()
			manual_tp_list()
			dislp_sel_pkg(TP_all_manual)
			pkg_conf_prompt(all_latest_pkg_download)
			print ('Do you want to include parser in the bundle?')
			yes_no('\nparser has to be included....\n', '\nno parser to include', parser_type_input)
			pkg_zip()
			print ('Do you want to create readme?')
			yes_no('\nReadme will be created\n', '\nReadme will not be created',readme_creation_prompt)
			break
		elif pkg_type_input == '3':
			exit()

# Second function to decide the packaging type if another Tech Pack to be included in the package			
def packaging_type_prompt1(): # Third prompt to get the packaging type
	print ('Please selct what type of packaging you need: Ex: 1 or 2 or 3')
	packaging_type = ["All latest tpi's", "Manual selection of tpi's","Exit_script"]# Dummy list for list types
	for (i, item) in enumerate(packaging_type, start=1):
		print(i,item,sep=' - ')
	while True:
		try:
			global pkg_type_input
			pkg_type_input = input("""Please specify '1' or '2' : """)
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		if pkg_type_input == '1':
			pkg_type_input = int(pkg_type_input)
			print ('')
			print ('The selected packaging type is ' + packaging_type[pkg_type_input-1])
			print ('')
			lst_in_selected_tp()
			all_latest()
			dislp_sel_pkg(TP_all_latest)
			pkg_conf_prompt(all_latest_pkg_download)
			break
		elif pkg_type_input == '2':
			pkg_type_input = int(pkg_type_input)
			print ('')
			print ('The selected packaging type is ' + packaging_type[pkg_type_input-1])
			lst_in_selected_tp()
			manual_tp_list()
			dislp_sel_pkg(TP_all_manual)
			pkg_conf_prompt(all_latest_pkg_download)
			break
		elif pkg_type_input == '3':
			break
def arg_passed():
	global arg1
	arg1 = None
	try:
		arg1 = sys.argv[1]
	except IndexError:
		pass
arg_passed()

# Dummy function
def dummyfunc():
	pass

#Function to pick package from local directory
def packagefromlocal():
	global packagecreation
	global TP_sel_input
	packagecreation = False
	
	while True:	
		try:
			global TP_sel_input
			TP_sel_input = input("Please specify the Tech Pack Name: ")
			TP_sel_input=TP_sel_input.upper()
			break
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
	
	if 'temp' in os.listdir('h:\\packaging'):
		print ('\nTemporary directory found, proceeding to zipping\n')
		for a in os.listdir('h:\\packaging\\temp\\'):
			for b in re.findall('(.*)_.*_.*', a):
				package_list.append(b)
# Packagelist file creation fucntion
		def package_list_creation():
			global readme_interfaces_list
			os.chdir('h:\\packaging\\temp')
			with open('packagelist.txt', 'w') as g:
				for h in package_list_order:
					for i in package_list:
						if i.startswith(h):
							g.write(i+'\n')
							if i.startswith('INTF_DIM') or i.startswith('INTF_DC'):
								if i not in readme_interfaces_list:
									readme_interfaces_list.append("%s" % i)
								else:
									pass
							else:
								pass
			g.close()
			os.system('dos2unix packagelist.txt')# To remove ^M/extra unwanted characters from the file|To convert data inside file into Bytecode

# To validate any DC or INTF present in temp directory
		for x in package_list_order:
			for y in os.listdir('h:\\packaging\\temp\\'):
				if y.startswith(x):
					packagecreation = True
				elif packagecreation != True:
					packagecreation = False

# Based on above validation the packagelist file creation fucntion is triggered					
		if packagecreation:
			package_list_creation()
		else:
			pass

		print ("Below are the files which will be included in the final zip package")
		for (i, item) in enumerate(os.listdir('h:\\packaging\\temp\\'), start=1):
			print(i,item,sep=' - ')
		yes_no('\nPackage zipped successfully', '\nExiting script...', dummyfunc)

		pkg_zip()

	else:
		print ('Temporary directory not found. Hence exiting the script...\n')
		exit

def cred_prompt():
	global user_name
	global pass_input
	user_name = ''
	pass_input = ''
	print ('\nFor packages to be downloaded from NEXUS, the script requires user XID and Password\n' + 'Please provide your credentials.')
	user_name = base64.b64encode(input("Please provide User name : ").encode("utf-8"))

	loginAttempts = 0
	
	# Code block to verify whether the given passwrod is correct or not
	while True:	
		try:
			pass_input = base64.b64encode(input("Please provide password : ").encode("utf-8"))
		except ValueError:
			print("Sorry, I didn't understand that.")
			continue
		
		s = os.popen('curl -s -u' + ' ' + base64.b64decode(user_name).decode("utf-8")+ ':"'+ base64.b64decode(pass_input).decode("utf-8")  + '" ' + main_url+'/').read()
		sl = str(s)
		
		if sl != '':
			break
		elif loginAttempts == 2:
			print ("Number of attempts expired")
			exit()
		elif sl == '':
			print ("Incorrect Username or Password\n")
			loginAttempts +=1
			continue
		else:
			print('Invalid Input')
			continue
	

# Function to take into consideration the argument passed as well to add multiple Tech Pack packaging
if arg1 == '-r':
	readme_creation_prompt()
elif arg1 == '-t':
	print ('\nPackage creation from temporary folder selected\n')
	packagefromlocal()
else:
	clean_up()
	def temp_prompt():
		cred_prompt()
		global TP_list
		global TP_list3
		global TP_list5
		global TP_all_latest
		global all_latest_download
		global sel_parser1
		global TP_list6
		global TP_all_manual
		global all_manual_tp_download
		TP_list = []
		TP_list3 = []
		TP_list5 = []
		TP_all_latest = []
		all_latest_download=[]
		sel_parser1 = []
		TP_list6 = []
		TP_all_manual = []
		all_manual_tp_download=[]
		TP_selection_prompt()
		packaging_type_prompt()
	def temp_prompt1():
		global TP_list
		global TP_list3
		global TP_list5
		global TP_all_latest
		global all_latest_download
		global sel_parser1
		global TP_list6
		global TP_all_manual
		global all_manual_tp_download
		TP_list = []
		TP_list3 = []
		TP_list5 = []
		TP_all_latest = []
		all_latest_download=[]
		sel_parser1 = []
		TP_list6 = []
		TP_all_manual = []
		all_manual_tp_download=[]
		TP_selection_prompt()
		packaging_type_prompt1()
	temp_prompt()