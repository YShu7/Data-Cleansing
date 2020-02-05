- [To approve/reject user account](#user_pending)  
- [To activate/deactivate user account](#user_approved)  
- [To assign the admin role](#user_admin)  
- [To create group](#group_create)  
- [To delete group](#group_delete)  
- [To view/download dataset](#dataset)  
- [To update data](#update_data)  
- [To view/download working report](#report)  
- [To view admin log](#log)

<hr/>

### To approve/reject user account <a name="user_pending"></a>
1. Navigate to page `User List`.  
> User should be able to see two section `Pending Users` and `Approved Users` in this page.
1. Scroll to the `Pending Users` section.  
> 
1. 
    ###### If you would like to approve the user account ######
    1. Click `Approve` to approve a user account.  
    > User should see approved user account added into the list of `Approved Users`.

    ###### If you would like to reject the user account ######
    1. Click `Reject` to reject a user account.  
    > The rejected account should be removed from the list.  

### To activate/deactivate user account <a name="user_approved"></a>
1. Navigate to page `User List`.  
> User should be able to see two section `Pending Users` and `Approved Users` in this page.
1. Scroll to the `Approved Users` section.  
> 
1. 
    ###### If you would like to activate an inactive user account ######
    1. Click `Activate` to activate the user account.  
    > User should see `Activate` button disabled and `Deactivate` button enabled. 
    > The color of the data should be updated to **BLACK**.

    ###### If you would like to deactivate an active user account ######
    1. Click `Deactivate` to deactivate the user account.  
    > User should see `Deactivate` button disabled and `Activate` button enabled. 
    > The color of the data should be updated to **RED**.

### To assign the admin role <a name="user_admin"></a>
1. Navigate to page `User List`.  
> User should be able to see two section `Pending Users` and `Approved Users` in this page.
1. Scroll to the `Approved Users` section.  
> 
1. Toggle the switch button `Admin` to make a user account to be admin or not.

### To create group <a name="group_create"></a>
1. Navigate to page `Groups`.  
> User should be able to see a list of groups.
1. Click `Create New Group`.
> User should be able to see a pop up window requesting for new group name.
1. Input new group name and click `Confirm`.
> The group name should **NOT** be the same as an existing group, otherwise the group will not be created and an error message will be thrown.

### To delete group <a name="group_delete"></a>
1. Navigate to page `Groups`.  
> User should be able to see a list of groups.
1. Click `Delete Group` to delete the group on the same line of the button.
> User should be able to see a pop up window requesting for the group to be deleted for confirmation.
1. Input group name and click the button to confirm deletion.
> The group name should be **EXACTLY** the same as the name shown in the list. Input should be **CASE-SENSITIVE**.
> Otherwise, if the group name doesn't match, an error message will be thrown.

### To view/download dataset <a name="dataset"></a>
1. Navigate to page `Dataset`.  
> User should be able to see a list of finalized data.
1. Select the group of the data under `Summary` to filter out only the data interested in.
> `Number of Data for #` and the data list should be updated respectively.
1. Click `Download all data` to download data from **ALL** groups as a `.csv` file.

### To update data <a name="update_data"></a>
1. Navigate to page `Update Data`. 
> User should be able to see a list of questions of data.
1. Input the keyword into `Search` field and click `Search` to filter out unrelated data.
>
1. Click on the question interested.
> An overview of all choices of the question should be expanded.
> User may click `Show More` or `Expand/Collapse All` to expand or collapse the answers.
1. Choose the answer that you think is the best for the question.  
> The selected answer should be highlighted with green.  
1. Click `Update` to submit the response.  
> User should be able to see a response message.

### To view/download working report <a name="report"></a>
1. Navigate to page `Working Report`.
> User should be able to see a list of individual report by default.
1. Click `Group` or `Individual` on the left top corner to switch between group and individual report.  
>
1. Click `Download Individual Report` to download **INDIVIDUAL** report as a `.xsl` file.
>

### To view admin log <a name="log"></a>
1. Navigate to page `Admin Log`.
> User should be able to see all admin actions on user account and data.
> A superuser should be able to see action logs done by all superusers and admins from **ALL** groups.