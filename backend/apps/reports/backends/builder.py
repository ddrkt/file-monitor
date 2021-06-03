from apps.file_tracking.models import File, FileStats, STAT_ATTRIBUTES
from apps.file_tracking.schemas import file_schema
from datetime import datetime, timedelta


class ReportBuilder:
    DEFAULT_REPORT_PERIOD = {'hours': 1}

    def get_report_qs(self, license_id, period=None):
        file_diffs = list()
        if period is None:
            period = self.DEFAULT_REPORT_PERIOD

        files = File.query.filter_by(license_id=license_id).filter(File.status.in_(['Active', 'Unavailable'])).all()
        start_datetime = self.get_start_datetime(period)
        for file in files:
            file_stats = FileStats.query.filter(
                FileStats.file_id == file.id,
                FileStats.date_created > start_datetime
            ).order_by(
                FileStats.date_created.asc()
            ).all()

            latest_stat = 'No stats collected in given period of time'
            diffs = list()
            for i in range(1, len(file_stats)):
                prev_stats = file_stats[i - 1]
                current_stats = file_stats[i]
                latest_stat = current_stats.date_created

                changed, diff = self.compare_stats(prev_stats, current_stats)
                if changed:
                    diffs.append(
                        {
                            'prev_date': prev_stats.date_created,
                            'current_date': current_stats.date_created,
                            'changes': diff
                        }
                    )
            file_diffs.append(
                {
                    'file': file_schema.dump(file),
                    'latest_stat': latest_stat,
                    'diff': diffs
                 }
            )
        return dict(start_datetime=start_datetime, diffs=file_diffs)

    @staticmethod
    def compare_stats(prev_stats, current_stats):
        stat_changed = False
        diff = list()

        for attr in STAT_ATTRIBUTES:
            attr_name = attr.get('name')
            prev_val = getattr(prev_stats, attr_name)
            current_val = getattr(current_stats, attr_name)

            if prev_val != current_val:
                stat_changed = True
                diff.append(
                    {
                        'prev_val': prev_val,
                        'current_val': current_val,
                        'attr_label': attr.get('label')
                    }
                )
        return stat_changed, diff

    @staticmethod
    def get_start_datetime(period):
        return datetime.today() - timedelta(**period)
