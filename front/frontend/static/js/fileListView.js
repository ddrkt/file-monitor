import AbstractView from './abstractView.js';

export default class extends AbstractView {

    initialize() {
        this.fileList = [];
    }

    resetFileList() {
        this.params.token = '';
        this.fileList = [];
        this.render();
    }

    async updateFileList(token) {
        this.params.token = token;
        const [data, status] = await this.makeRequest('/files', 'GET');
        if (status === 200) {
            this.fileList = data;
            this.render();
        }
    }

    getFileListView() {
        let view = ``;
        this.fileList.forEach(file => {
            view += `<tr data-id="${file.id}">
                        <td class="path-cell">${file.file_path}</td><td class="status-cell">${file.status}</td>
                     </tr>`
        });
        return view;
    }

    getView() {
        return `
            <table class="file-list-table">
                <thead class="file-list-header">
                    <tr><th class="path-cell">File path</th><th class="status-cell">Status</th></tr>
                </thead>
                <tbody id="list" class="file-list-body">
                    ${this.getFileListView()}
                </tbody>
            </table> 
        `
    }
}
