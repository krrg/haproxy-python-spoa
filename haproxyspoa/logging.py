import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)

logger = logging.getLogger(__name__)


class FlowIdLoggerAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        return f"[{self.extra['flow_id']}] {msg}", kwargs