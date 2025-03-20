import argparse
import json
import sys

from framework.core.utils.logger import logger
from framework.runner.runtime import karta_runtime

logger.info('***************** Initializing Karta.py ********************')


def karta_main(args=None):
    try:
        arg_parser = argparse.ArgumentParser(usage="Karta.py - pass tags or features to run")
        group = arg_parser.add_argument_group('Run', 'Run arguments group')
        # group.add_mutually_exclusive_group(required=True)
        # arg_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-t", "--tags", help="Tags to run", type=str, nargs='+')
        group.add_argument("-f", "--features", help="Features to run", type=str, nargs='+')
        parsed_args = arg_parser.parse_args(args=args)

        run_results = None
        if parsed_args.tags:
            logger.info("Tags to run {}".format(parsed_args.tags))
            run_results = karta_runtime.run_tags(parsed_args.tags)
        elif parsed_args.features:
            logger.info("Features to run {}".format(parsed_args.features))
            run_results = karta_runtime.run_feature_files(parsed_args.features)
        else:
            print("Error either tags or features needs to be passed to run", file=sys.stderr)
            arg_parser.print_help(sys.stderr)

        logger.debug("Run results are " + str(run_results))
        for feature_result in run_results.feature_results:
            logger.info(
                "Result of " + str(feature_result.source) + " is " + "passed" if feature_result.is_successful() else (
                    "errorred" if feature_result.error else "failed"))

    except Exception as ex:
        print("Exception occurred" + str(ex), file=sys.stderr)
