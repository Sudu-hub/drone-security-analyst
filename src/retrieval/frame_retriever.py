class FrameRetriever:

    def __init__(self, repository):
        self.repository = repository

    def get_all(self):
        return self.repository.get_all_observations()

    def search_object(self, object_type):
        return self.repository.search_by_object(
            object_type
        )

    def search_time(
        self,
        start_timestamp,
        end_timestamp
    ):
        return self.repository.search_by_time(
            start_timestamp,
            end_timestamp
        )