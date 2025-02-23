# [Selenium Automation Script](https://pypi.org/project/PBI-SELENIUM/#description)

This Python script utilizes Selenium for web automation to perform tasks related to logging in, updating workspace reports, and downloading reports.

## Prerequisites

- Python installed (version 3.x recommended)
- Power BI Account

## Features

### 1. UpdateWorkspace
Updates the specified workspace.

```python
from PBI-SELENIUM import Routine 

Login = 'example@gmail.com'
Password = 'example123'
Workspace = 'https://app.powerbi.com/groups/me/list?experience=power-bi'

Routine.UpdateWorkspace(Login, Password, Workspace)
```

### 2. DownloadReport
Downloads reports from specified links.

```python
from PBI-SELENIUM import Routine 

Login = 'example@gmail.com'
Password = 'example123'
Workspace = 'https://app.powerbi.com/groups/me/list?experience=power-bi'
links = ['YourDashboardLink', 'https://app.powerbi.com/groups/me/reports/ReportSection?experience=power-bi']

Routine.DownloadReport(Login, Password, Workspace, links)
```

### 3. ViewReports
Views reports at regular intervals.

```python
from PBI-SELENIUM import Routine 

Login = 'example@gmail.com'
Password = 'example123'
Workspace = 'https://app.powerbi.com/groups/me/list?experience=power-bi'
interval = 10  # interval time between reports
links = ['https://app.powerbi.com/groups/me/reports/ReportSection?experience=power-bi']

Routine.ViewReports(Login, Password, Workspace, interval, links)
```

