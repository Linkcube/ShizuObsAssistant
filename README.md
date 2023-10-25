# ShizuObsAssistant

This program manages a 'ledger' of DJs and Promotional videos used for stream, that can be selectively added to a 'lineup'. Once the lineup is complete, it can be exported to a json file for use in the accompanying OBS plugin to generate scenes for each of the selected DJs and promos. If you are using an existing ledger and lineup, make sure to load the ledger then lineup, either through the menu or home buttons, before continuing. To add a new DJ entry, click on the Add menu > New DJ Entry, which will bring up the new entry edit window to be filled in. Adding to lineup will not save or exit the current entry, make sure to save once you're done! Likewise, the process is similar for adding promotional videos, which only have a name and recording path to manage.

On the ledger page, you can edit/delete entries for DJs or Promotional videos by double cicking a row, once you are done making any changes make sure to save though the Program menu > Save Ledger button.

The lineup page will let you set the order to DJs and Promotional videos after adding them, you can edit DJ entries to either be live or pre-recorded, but otherwise you can only delete these entries after double clicking. Once you are done setting up your lineup, make sure to export using Program menu > Export Lineup. This will save the file either for later loading/edits or for use in the OBS plugin.

When saving or exporting data, a backup will be made in a subdirectory of where this file is, along with the date+time it was saved. Resetting the data will only clear the ledger/lineup in memory, files are not changed.

Thanks for using the program, make sure to report any issues with the software.
