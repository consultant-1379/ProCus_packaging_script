======================================================

Copyright Ericsson Radio System $Current_year$

Tar file name : $TP_zip_name$

Creation Date : $Creation_Date$

=======================================================


Reason for delivery:
===================
Delivery of Ericsson $TP_name$ Measurement Tech packs


This Specific Package corrects the following TRs/CRs/WP/WI:
==========================================================
$TR_name$


Previous ECs from this RSTATE Release correct the following issues:
===================================================================
N/A


Known Faults/Limitations:
=========================
-

Dependencies:
=============

Note: 	It is presumed that the Customer Site has a working Ericsson Network IQ Server(*), 
      	and that all known limitations and workarounds have been carried out.
	
Note:	All commands below should be run as "root" user, unless otherwise specified.
$DIM_E_CN_depend$

==================================
Section 1: Pre-Installation Tasks:
==================================

Note :	Prior to installation, a snapshot of the system must be taken.	
		Steps to take snapshot on Rack/Single Blade/Multi Blade deployments are detailed 	
		in the ENIQ Statistics System Administration Guide (SAG) available in the CPI.	
		
		Refer to the CPI applicable for the installed ENIQ release.
		
		After taking snapshot of the system execute the following steps to install the Tech Pack.
		Ensure that the ENIQ rolling snapshot service is disabled before Tech Pack Installation.

		*(In case of MultiBlade, Run the below steps on Coordinator blade unless specified)*
		
		
1.1 Make a temporary directory on the ENIQ server:
	# mkdir -m 777 -p /var/tmp/ENIQ_PC_upgrade


1.2 Download the EU zip file from GASK to the temporary directory created in 1.1 and unzip it
	# cd /var/tmp/ENIQ_PC_upgrade
	# /usr/bin/unzip 19090-$TP_product_number$_X_$Eridoc_revision$_PKZIPV2R04.zip
      

1.3	Check that services are online on each blade in the deployment:
    • ENIQ Statistics Coordinator Server
    • ENIQ Statistics Engine Server
	• ENIQ Statistics Reader Server(s)
	
	# bash /eniq/admin/bin/manage_deployment_services.bsh -a list -s ALL

1.4	Change user permisson for packagelist.txt and update_feature_list.sh
	# chmod 777 /var/tmp/ENIQ_PC_upgrade/update_feature_list.sh
	# chmod 777 /var/tmp/ENIQ_PC_upgrade/packagelist.txt

	
1.5	Switch user to dcuser for installation steps below.
	# su - dcuser


=====================================
Section 2:  Installation of licenses:
=====================================


*(In case of MultiBlade, Run this below steps on Coordinator blade )
Note: In this section, step 2.1 is optional and should only be executed if license installation is required.
Otherwise, skip to step 2.2


2.1	execute the below giving full path of the license file including the filename 
	# cd /eniq/sw/bin/
	# ./licmgr -install <full path to licensefilename>
	
2.2 execute the below steps to update the features for licenses
	# cd /var/tmp/ENIQ_PC_upgrade
	# ./update_feature_list.sh
	
=================================
Section 3:  Package Installation:
=================================
In case of MultiBlade, Run the below steps on Coordinator Blade unless specified other wise


3.1	Parser Install
	$Parser$


3.2  Copy the tech packs from the folder /var/tmp/ENIQ_PC_upgrade to /eniq/sw/installer
     # cp /var/tmp/ENIQ_PC_upgrade/*.tpi /eniq/sw/installer/
     # cp /var/tmp/ENIQ_PC_upgrade/packagelist.txt /eniq/sw/installer/


3.3	Install all topology and measurement tech packs using the below command
	Installation of Tech packs without dependency checking is required for successful
	completion of the upgrade.
	# cd /eniq/sw/installer      	
	# ./tp_installer -p . -f packagelist.txt


3.4	Interface Activation. The interfaces should now be activated
	with the correct <eniq_oss_name>
	$Interface_activation$


3.5	Exit from dcuser
	# exit

===================================
Section 4: Post-Installation Steps:
===================================


4.1	Check that services are online
	# bash /eniq/admin/bin/manage_deployment_services.bsh -a list -s ALL


4.2	Restart all the ENIQ services and set profile to Normal

	In case of MultiBlade, Run this step on Coordinator blade
	# cd /eniq/admin/bin
	# /usr/bin/bash ./manage_deployment_services.bsh -a restart -s ALL

4.2.1  	In case of Multi Blade run this on the Engine blade only.
	# /usr/bin/su - dcuser -c "engine -e changeProfile Normal"


4.3	Enable the ENIQ rolling snapshot service 
	For MultiBlade, Below steps has to be followed on all the four blades in sequence [ Coordinator, Engine , Reader_1, Reader_2]. 	
 	# bash ./manage_eniq_services.bsh -a start -s roll-snap


4.3.1	Check that services are online on each blade in the deployment:
    • ENIQ Statistics Coordinator Server
    • ENIQ Statistics Engine Server
	• ENIQ Statistics Reader Server(s)
	
	# bash /eniq/admin/bin/manage_deployment_services.bsh -a list -s ALL

	
4.4 The directories from which the topology and measurement files are fetched are described in
	$Tech_Pack_User_Guide_name$ ($Tech_Pack_User_Guide_number$ LATEST).
	
	Manually create the Topology directories as dcuser. They must be created as specified in the User Guide
	

===============================
Section 5: Universe decryption:
===============================


$Universe$


=================================
Section 6: Rollback Instructions:
=================================


NOTE:	If the procedure in Section 3 was successful, Skip to Section 7.
	If the procedure failed, rollback to the previously created snapshots by following
	the steps mentioned in Ericsson Network IQ Statistics System Administration Guide (4/1543-CSA 113 63/1)


==========================
Section 7: Clean-Up Steps:
==========================

	When satisfied that the procedure was successful, the created snapshots should be deleted:

7.1	Clean-Up steps on Rack Servers : 

7.1.1	# cd /eniq/admin/bin
	# /usr/bin/bash /eniq/bkup_sw/bin/manage_zfs_snapshots.bsh -a delete -f ALL=<snap_label>
	When prompted, enter 'Yes' to confirm deletion of snapshots.
	
7.2	Clean-Up steps on Single or Multi Blade Servers	

7.2.1	Delete ZFS Snapshots
	Incase of Multi Blade the below step needs to be executed on all 4 blades in sequence [Coordinator, Engine, Reader_1, Reader_2]
	# cd /eniq/bkup_sw/bin
	# bash ./manage_fs_snapshots.bsh -a delete -f ALL=<snap_label>

	When prompted, enter 'Yes' to confirm deletion of snapshots.

7.2.2	Delete NAS Snapshots
	Incase of Multi Blade the below step needs to be executed on Coordinator blade
	# cd /eniq/bkup_sw/bin
	# bash ./manage_nas_snapshots.bsh -a delete -f ALL -n <snap_label>

7.2.3	Delete SAN Snapshots
	Incase of Multi Blade the below step needs to be executed on Coordinator blade
	# cd /eniq/bkup_sw/bin
	# bash ./manage_san_snapshots.bsh -a delete -f ALL -n <snap_label>

7.3 If you wish, you can move the tar file to another location on your server. Then you should
	remove the created directory and its contents from the /var/tmp directory.
	# cd /var/tmp/
	# rm -rf ENIQ_PC_upgrade


7.4 Remove old tpi files from /eniq/sw/installer. Remove temporary universe files if applicable.
	# su - dcuser
	# ls /eniq/sw/installer/*.tpi
	# rm /eniq/sw/installer/*.tpi
	# rm -rf /eniq/sw/installer/BO_tmp
	# rm -rf /eniq/sw/installer/boreports
	# exit
