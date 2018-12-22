"""ACSG game"""
import json
import logging
import dallinger

logger = logging.getLogger(__file__)
config = dallinger.config.get_config()


def extra_parameters():
    config.register('n', int)
    config.register('num_players', int)
    config.register('game_duration', int)
    config.register('include_human', bool)
    config.register('bot_strategy', str)
    config.register('rows', int)
    config.register('columns', int)
    config.register('num_food', int)
    config.register('visibility', int)
    config.register('bot_motion_rate', int)
    config.register('block_size', int)
    config.register('block_padding', int)
    config.register('seed', str)
    config.register('max_payoff', float)


class Griduniverse2(dallinger.experiment.Experiment):
    """Define the structure of the experiment."""

    def __init__(self, session=None):
        """Initialize the experiment."""
        super(Griduniverse2, self).__init__(session)
        self.num_players = config.get("num_players")
        self.game_duration = config.get("game_duration")
        self.include_human = config.get("include_human")
        self.bot_strategy = config.get("bot_strategy")
        self.rows = config.get("rows")
        self.columns = config.get("columns")
        self.num_food = config.get("num_food")
        self.visibility = config.get("visibility")
        self.bot_motion_rate = config.get("bot_motion_rate")
        self.block_size = config.get("block_size")
        self.block_padding = config.get("block_padding")
        self.seed = config.get("seed")
        self.max_payoff = config.get("max_payoff", 5.0)
        self.experiment_repeats = 1
        self.initial_recruitment_size = config.get("n")
        if session:
            self.setup()

    def create_network(self):
        """Return a new network."""
        return dallinger.networks.Empty(max_size=10000)

    def recruit(self):
        """Recruitment."""
        if not self.networks(full=False):
            self.recruiter.close_recruitment()

    def bonus(self, participant):
        """The bonus to be awarded to the given participant.

        Return the value of the bonus to be paid to `participant`.
        """
        infos = participant.infos()
        if not infos:
            return 0.0
        data = infos[0].contents
        if not data:
            return 0.0
        try:
            data = json.loads(data)
        except (TypeError, ValueError):
            logger.info("Could not parse compressed ACSG data")
            return 0.0
        # Returns a value between 0.00 and max_payoff
        logger.info("Experiment data: {}".format(data))
        try:
            payoff = float(data.get('data', {}).get('payoff', 0.0))
        except (TypeError, ValueError):
            logger.info("Could not parse payoff value")
            return 0.0
        if payoff > self.max_payoff:
            logger.info("Payoff greater than maximum, limiting.")
            return self.max_payoff
        if payoff < 0.0:
            logger.info("Payoff less than zero, limiting.")
            return 0.0
        return payoff

    def bonus_reason(self):
        """The reason offered to the participant for giving the bonus.
        """
        return (
            "Thank you for participating! You earned a bonus based on your "
            "performance in Griduniverse!"
        )
