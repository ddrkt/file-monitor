import ReportBuilder from './reportBuilder.js';
import TokenControlsView from './tokenControls.js';
import ReportControlsView from './reportControls.js';
import FileListView from './fileListView.js';

document.addEventListener('DOMContentLoaded', () => {
    const tokenControlsView = new TokenControlsView('#auth-controls');
    const reportControlsView = new ReportControlsView('#report-controls');
    const reportView = new ReportBuilder('#reports');
    const fileListView = new FileListView('#files');

    tokenControlsView.on('tokenChange', (state) => {
        reportControlsView.setActiveState(state);
        reportView.clearReport();
        if (state) {
            fileListView.updateFileList(tokenControlsView.getToken());
        } else {
            fileListView.resetFileList();
        }
    });
    reportControlsView.on('getReport', (period) => {
       reportView.getReport(period, tokenControlsView.getToken());
    });
    reportView.on('reportRendered', () => {
       reportControlsView.setLoadState(false);
    });

    tokenControlsView.render();
    reportControlsView.render();
    reportView.render();
    fileListView.render();
});
