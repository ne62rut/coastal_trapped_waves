# coastal_trapped_waves

# How to process

. gesla_processing_australia2023addon.ipynb 
    takes high-frequency tide gauge records from GESLA 3, averages them as hourly records, select for a specific year and region, smooths them by means of a lowess filter to remove tide contributions and correct them for the Dynamic Atmospheric Correction. The whole processing is needed to make GESLA dataset comparable to altimetry estimations. This particular code is adapted to process tide gauges in Australia for 2023, which are not yet part of GESLA 3. The original general code is gesla_processing.ipynb
    
. model_data_reader.ipynb
    takes data from the bluelink reanalysis and saves them as daily grids similar to SWOT format 

. create_filtered_time_series_tg.ipynb 
    isolates a set of TGs in Australia and filter them (saving the filtered version externally)
    
    
. create_filtered_time_series.py
    takes L4 products and create for each grid point a time series filtered in time, which is saved separately
    
. create_filtered_grids.py 
    from the output of 3. reconstructs a daily L4 product, containing the signal filtered in time. There is also a ipynb version of it showing some plots.
    
. correlate_tg_with_grids.ipynb
    takes the output of 2. (filtered tide gauges time series) and 3. (filtered altimetry time series) and correlate them, by offering the possibility to select a lag correlation

. correlate_tg_with_grids_1d.ipynb 
    compare the time series with a filtered version of CMEMS and SWOT maps at the closest location to the tide gauges
    
. phase_speed_computation.ipynb 
    compare the Hovmoller diagrams of the filtered signals and compute the phase speed with the radon transform


# Diary

16.01.2025
I have started EOF_analysis. it seems to work for bluelink, but I don't know why it is not working for SWOT...probably something to do with the grid points coordinates? I am trying to isolate points closer than 20 or 50 km to the coastline, but they seem to be too few for SWOT...

15.01.2025
Hovmoller diagrams created with phase speed computed, in phase_speed_computation.ipynb

28.11.2024
I have created correlate_tg_with_grids_1d.ipynb as described below, but I have expanded it also to include the model time series. Then, I should do the analysis of the Hovmoller diagrams computing the phase speed and possibly the EOF analysis

24.10.2024
Next step is to put the correlation analysis from analyse_tg_ctw_withswot.ipynb on a separate independent code. And then in yet another code the analysis of the Hovmöller diagrams. We can call it correlate_tg_with_grids_1d.ipynb


23.10.2024
temp_phase_speed_computation was written to demonstrate synthetically that, given a Hovmöller diagram, we can compute the phase speed of a Kelvin wave. 
I want to separate analyse_tg_ctw_withswot.ipynb in different functions that use the fact that I am saving externally the filtered time series. First of all, I separate the isolation and filtering of the tide gauges. This is now done in create_filtered_time_series_tg.ipynb. The next step is to remove those blocks from analyse_tg_ctw_withswot.ipynb and do the computations of that code by loading the externally created datasets.

22.10.2024
create_filtered_time_series has been extended to include bluelink data. general_checks.ipynb was created as a quit tool to check outputs

21.10.2024

I wrote to Ballarotta and sammy.metref@datlas.fr. They have a version of MIOST without SWOT, but unfortunately also without SWOT Nadir and Altika. Still interesting to understand the impact of the interpolation method rather than of SWOT. I have put the data into DGFI8/D/SWOT_L4 as "mapping_0.0_360.0_-80.0_90.0_20230228_20230730_c2n_h2b_j3n_s3a_s3b_s6a_hr_component_geos_barotrop_eqwaves_lwe"
But I should also analyse the model data (bluelink ocean reanalysis), which I have put into /DGFI8/D/sealevel/bluelink_oceanreanalysis.
I am writing model_data_reader.ipynb in order to save the bluelink data in the same format of SWOT data, as daily grid files, but I have difficulties in changing the naming of the dimensions from xt,yt to longitude and latitude...



15.10.2024

Keep in mind that we are using the "Experimental Multimission Level-4 maps with SWOT" from https://www.aviso.altimetry.fr/en/news/front-page-news/news-detail.html?tx_ttnews%5Btt_news%5D=2991&cHash=657ff58f9f96f01b4c57b484d7818567
From the user manual available I understand that this is NOT using 4D-Var, which is only used in the North Atlantic. Instead, the method used in MIOST (Multiscale Inversion of Ocean Surface Topography)...is it any different from the method used inthe standard CMEMS maps? The correct reference to read is https://doi.org/10.5194/egusphere-2024-2345 . Note also that these grids are just 1/10 of a degree!
I have put an option to add lag correlation in correlate_tg_with_grids. I should make a video of 0 to 5 days. What I am missing now is to put the model in, and to compute the speed.
I should consider writing to florian.leguillou@datlas.fr to get the 4D-VAR with and without SWOT.

11.10.2024

From analyse_tg_ctw_withswot.ipynb, which is too long, I want to save filtered tide gauge time series in a folder called filtered_time_series_tidegauges. I will do this later, for now I have added a section in the same notebook, where the correlation of each tide gauge against the SWOT filtered data is shown. But it takes time, so I should externalise it, once I have saved the filtered tide gauge time series. I externalise it in a notebook called "correlate_tg_with_grids.ipynb"



02.10.2024

I have copied the first part of the function into a create_filtered_time_series.py code and I am launching it to have a first complete run, then I can see if I can speed up the code. I have copied the second part in create_filtered_grids.py, but it takes 2 minutes per day, which is a bit too long...I am launching it anyway. Once I have the dataset the next step would be to correlate with tide gauge.



01.10.2024

For now in create_filtered_grids there are two parts. One that save separately every filtered time series and the other that builds back the filtered daily grids. For now, they are just test files. The second part seems quick enough. But the first part is taking 72 seconds for 100 successful points. We may have 10000 successfull points, so it could be too slow?


30.09.2024

My next objective is to check the correlation of key tide gauges agains the filtered signal of the altimetry grids. This was done pointwise in analyse_tg_ctw_withswot.ipynb, but I would like to do it spatially. Firstly, I have to create a local filtered gridded dataset of the altimetry grids. 
In order to do this, I create a notebook called create_filtered_grids. I will have to save separetely every filtered time series and then try to create a new daily grid using each point of the different time series...is this realistic? 





## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.lrz.de/dgfi-tum/work_passaro/coastal_trapped_waves.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.lrz.de/dgfi-tum/work_passaro/coastal_trapped_waves/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
