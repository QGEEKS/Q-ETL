# Frequently Asked Questions (FAQ)

### What is Q-ETL?
Q-ETL is a tool designed for ETL (Extract, Transform, Load) processes using QGIS. It simplifies data manipulation and integration tasks.

### How do I install Q-ETL?
1. Download the latest release from [GitHub](https://github.com/QGEEKS/Q-ETL/releases).
2. Unzip the archive to your desired location.
3. Follow the setup instructions in the `getting_started.md` file.

### What are the system requirements?
- **Operating System**: Windows 10 or later
- **Python Version**: 3.8 or higher
- **QGIS Version**: 3.16 or higher

### Where can I find the logs?
Logs are stored in the directory specified in the `settings.json` file under the `logdir` key.

### How do I report an issue?
You can report issues on the [GitHub Issues page](https://github.com/QGEEKS/Q-ETL/issues). Please include:
- A detailed description of the problem.
- Steps to reproduce the issue.
- Any relevant log files or screenshots.

### Will QETL run on Mac og Linus
Unortiunetly no. The project depends on the OsGeo4W platform - where the W implies Windows. There is no equivalent to the OsGeo4W suite on linux and Mac, which means that we can not run QETL on those platdforms.

