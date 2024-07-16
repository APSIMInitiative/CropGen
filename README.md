# CropGen

A crop design optimisation platform to optimise and quantify trade-offs of cropping strategies.

## About the project 
 
CropGen is a tool connecting the APSIM sorghum crop growth model with an optimisation platform to facilitate exploration and optimisation of the performance of a number of design factors (e.g., maturity, tillering), with respect to relevant production criteria (e.g., yield, risk, water use). CropGen generates a set of optimal solutions, i.e., combinations of the design factors specified, representing the full spectrum of trade-offs of the criteria of interest, allowing for different preferences and circumstances to be represented. By making use of the optimisation framework, CropGen allows for high dimensionality problems and scenarios to be explored more comprehensively and efficiently than traditional methods.

A schematic of the CropGen optimisation platform is shown below. 

![image](https://github.com/user-attachments/assets/e817cf4b-6c10-4c39-94c0-18355f297b03)

## Implementation 

CropGen is provided as a stand-alone application. It is written in Python and can be containerized. It has been tried and tested using Docker. The Dockerfile has been provided, which can be built to create the Docker image. To integrate CropGen into a fully functional system, the following additional applications are required:

* APSIM Crop Growth Model – For running simulations.
* Results Server – For invoking CropGen and for storing the results.

CropGen uses a JSON configuration file (CropGen\lib\config\config.json) to specify the application configuration. Each configuration entry can be overridden, to use a different value when running inside Docker, by appending Docker to the end of the entry, for example: 

```
"SocketServerHost": "localhost",    
"SocketServerHostDocker": "0.0.0.0",
```

### API

***RunJobRequest***

To run CropGen, a RunJobRequest message (CropGen\lib\models\run\run_job_request.py) should be sent. If a job is currently running, or the format of the message is invalid, an error will be returned (CropGen\lib\models\run\run_crop_gen_response.py), otherwise the run  will commence. 

To connect to APSIM, CropGen will create a socket connection, using the RunJobRequest, to extract the CGMServerHost and CGMServerPort. To run APSIM, CropGen will send RelayApsim messages (CropGen\lib\models\cgm\relay_apsim.py), until all iterations have been processed. Each iteration, CropGen will send an IterationResults message (CropGen\lib\models\rest\iteration_results_message.py) to the Results Server. Once all iterations have been processed, a FinalResults message (CropGen\lib\models\rest\final_results_message.py) will be sent. 

The results messages will be sent using REST PUT calls (CropGen\lib\utils\results_publisher.py). The URLs for these are sent as part of the RunJobRequest (IterationResultsUrl and FinalResultsUrl). It is up to the Results Server to consolidate this data into the desired output format and allow these results to be downloaded.

***GetStatus***

To get the status of CropGen, a Status message can be sent to CropGen. The response will contain information about any running jobs.

***GetConfig*** 

To get the status of CropGen, a GetConfig message can be sent to CropGen. The response will contain the configuration that is currently loaded.

***SetConfig***

To set the CropGen configuration, a SetConfig message can be set to CropGen. This will overwrite the running configuration.

## Example System Implementation 

The following diagram shows an example of a full system implementation, with an example sequence diagram to illustrate a job being run.

**Example Full System Implementation**

![image](https://github.com/user-attachments/assets/f0aa5006-c189-4514-ac5a-577ad8679a91)

**RunJob Sequence Diagram**

![image](https://github.com/user-attachments/assets/b4664b4e-323f-44d7-9d58-8c2bb57349c0)

