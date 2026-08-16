from bog_simulator.ui import app

from bog_simulator.core import vessel, environment
from bog_simulator.core.consumers import megi, dfde, gcu, consumer

from bog_simulator.utils import data_loader

def main() -> None:
    vessel_config = data_loader.load_vessel_data()
    enviroment_variables = data_loader.load_weather_variables()

    megi_models = [megi.MEGI(**megi_params) for megi_params in vessel_config["Main_Engines"]]
    dfdes_model = [dfde.DFDE(**dfde_params) for dfde_params in vessel_config["Diesel_Generators"]]
    gcu_model = gcu.GCU(**vessel_config["Gcu"])
    enviroment_model =  environment.Environment(vessel_config["vessel"], enviroment_variables)
    model_consumers = consumer.Consumers(dfdes_model, megi_models, gcu_model)
    vessel_model = vessel.LNGc(vessel_config["tanks"], enviroment_model, model_consumers, 0)
    

    Application = app.Simulation_GUI(vessel_model)
    Application.run()

if __name__ == "__main__":
    main()
