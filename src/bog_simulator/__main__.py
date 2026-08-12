from bog_simulator.ui import app

from bog_simulator.core import vessel, environment

from bog_simulator.utils import data_loader

def main() -> None:
    vessel_config = data_loader.load_vessel_data()
    enviroment_variables = data_loader.load_weather_variables()

    enviroment_model =  environment.Environment(vessel_config["vessel"], enviroment_variables)
    vessel_model = vessel.LNGc(vessel_config["tanks"], enviroment_model, -3200, 0)

    Application = app.Simulation_GUI(vessel_model, enviroment_model)
    Application.run()

if __name__ == "__main__":
    main()
