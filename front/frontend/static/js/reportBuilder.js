import AbstractView from './abstractView.js';

export default class extends AbstractView {
    reportsEndpoint = 'reports'

    unsetParams() {
        this.params.period = null;
        this.params.token = null;
    }

    initialize() {
        this.unsetParams();
    }

    getReport(period, token) {
        this.params.period = period;
        this.params.token = token;
        this.render();
    }

    clearReport() {
        this.unsetParams();
        this.render();
    }

    onRender() {
        this.unsetParams();
    }

    async requestReportQuery() {
        return await this.makeRequest(this.reportsEndpoint, 'POST', this.params.period);
    }

    getReportView(reportQuery) {
        let reportViewString = '';
        const fileDiffs = reportQuery.diffs;
        reportViewString += `
            <div class="header">
                <h1>Report from ${reportQuery.start_datetime}</h1>
                <p>Files in tracking: <b>${reportQuery.diffs.length}</b></p>
            </div>
        `;

        fileDiffs.forEach(fileDiff => {
            const file = fileDiff.file;
            const diff = fileDiff.diff;
            reportViewString += `
                <hr class="file-separator"/>
                <div class="file-info">
                    <p>File path: <b>${file.file_path}</b></p>
                    <p>Current file status: <b>${file.status}</b></p>
                    <p>Latest stat record datetime: <b>${fileDiff.latest_stat}</b></p>
                </div>
            `;

            diff.forEach(change => {
                reportViewString += `
                    <p class="change-header">
                        Changes made between <b>${change.prev_date}</b> and <b>${change.current_date}</b>
                    </p>
                    <table class="change-table" border="2">
                    <thead>
                        <tr><th>What changed</th><th>Previous value</th><th>Current value</th></tr>
                    </thead>
                    <tbody>
                `;

                change.changes.forEach(row => {
                    reportViewString += `
                        <tr><td>${row.attr_label}</td><td>${row.prev_val}</td><td>${row.current_val}</td></tr>
                    `;
                });
                reportViewString += '</tbody></table>';
            });
        });
        return reportViewString;
    }

    async getView() {
        if (!this.params.token || !this.params.period) {
            return `
                <p id="report-placeholder">No data</p>
            `;
        }
        const [data, status] = await this.requestReportQuery();
        if (status !== 200) {
            return this.getErrorView(data.error);
        }
        this.trigger('reportRendered');
        return this.getReportView(data);
    }
}
