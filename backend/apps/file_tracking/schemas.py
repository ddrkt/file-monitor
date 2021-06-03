from project import serializers
from apps.file_tracking.models import File, FileStats


class FilesSchema(serializers.SQLAlchemyAutoSchema):
    class Meta:
        model = File
        fields = ('id', 'file_path', 'status', 'license_id')


class FileStatsSchema(serializers.SQLAlchemyAutoSchema):
    class Meta:
        model = FileStats
        fields = ('id', 'file_id', 'mode', 'nlink', 'user', 'group', 'size', 'mtime', 'ctime', 'flags')


file_schema = FilesSchema()
files_schema = FilesSchema(many=True)
file_stat_schema = FileStatsSchema()
file_stats_schema = FileStatsSchema(many=True)
