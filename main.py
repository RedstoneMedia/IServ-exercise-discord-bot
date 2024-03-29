import autoIserv
from autoIserv.Exercise import Exercise
import bot

import argparse
import json
import os
import time
import pathlib
import logging
from selenium.common.exceptions import WebDriverException

from multiprocessing import Process


def is_exercise_new(exercise : Exercise, folder="exercises"):
    for file in os.listdir(folder):
        if Exercise.load(f"{folder}/{file}") == exercise:
            return False
    return True


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--config", default="config.json", required=False, help="The path to the config file", type=str)
    args = arg_parser.parse_args()
    config = json.load(open(args.config, encoding="utf-8"))

    logging.basicConfig(filename=config["LogFile"], format='%(asctime)s %(message)s', level=logging.ERROR)
    try:
        config["ExercisesFolder"] = os.path.expandvars(config["ExercisesFolder"])
        config["AttachmentDownloadDir"] = os.path.expandvars(config["AttachmentDownloadDir"])
        config["CredentialPath"] = os.path.expandvars(config["CredentialPath"])
        pathlib.Path(config["ExercisesFolder"]).mkdir(parents=True, exist_ok=True)
        pathlib.Path(config["AttachmentDownloadDir"]).mkdir(parents=True, exist_ok=True)
        key = config["SecretCredentialPassword"]

        bot_process = Process(target=bot.run, args=(config,))
        bot_process.start()

        session = None
        while True:
            try:
                session = autoIserv.login(config["CredentialPath"], key, headless=True, iserv_url=config["IServUrl"])
                exercise_module = autoIserv.Modules.ExerciseModule(session)

                while True:
                    exercises = exercise_module.get_exercises()

                    for exercise in exercises:
                        if is_exercise_new(exercise, config["ExercisesFolder"]):
                            exercise.view(download_attachments=True)
                            exercise.save(config["ExercisesFolder"], attachment_dir=os.path.expandvars(config["AttachmentDownloadDir"]))

                    print("[*] Sleeping")
                    time.sleep(config["UpdateInterval"])
            except WebDriverException as e:
                if session != None:
                    session.close()
                logging.error("[*] Restarting due to web driver error", exc_info=e)
    except Exception as e:
        logging.error(f"Fatal exception", exc_info=e)


if __name__ == "__main__":
    main()