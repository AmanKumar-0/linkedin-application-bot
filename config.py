# # General bot settings

# # browser you want the bot to run ex: ["Firefox"], ["Chrome"] choose one only
# browser = ["Chrome"]
# # Optional! run browser in headless mode, no browser screen will be shown it will work in background.
# headless = True
# # Optional! for Firefox enter profile dir to run the bot without logging in your account each time
# firefoxProfileRootDir = r""
# # If you left above field empty enter your Linkedin password and username below
# # Linkedin credits
# email = "amanhuriya2@gmail.com"
# password = ""

# # These settings are for running Linkedin job apply bot
# LinkedinBotProPasswrod = ""
# # location you want to search the jobs - ex : ["Poland", "Singapore", "New York City Metropolitan Area", "Monroe County"]
# # continent locations:["Europe", "Asia", "Australia", "NorthAmerica", "SouthAmerica", "Africa", "Australia"]
# location = ["Europe", "Asia", "Australia", "NorthAmerica", "SouthAmerica", "Africa", "Australia"]
location = ["India"]
# # keywords related with your job search
# keywords = ["lead developer", "chief technical officer", "cto", "python","Software Engineer", "Full Stack Developer", "Senior Software Engineer", "Tech Lead", "Engineering Manager", "Backend Developer", "Backend Engineer", "Frontend Developer", "Frontend Engineer", "Web Developer", "Web Engineer", "Python Developer", "Python Engineer", "Node.js Developer", "Node.js Engineer", "React Developer", "React Engineer", "Django Developer", "Django Engineer", "Flask Developer", "Flask Engineer", "DevOps Engineer", "Site Reliability Engineer", "SRE", "Cloud Engineer", "AWS Engineer", "Azure Engineer", "GCP Engineer", "Data Engineer", "Machine Learning Engineer", "ML Engineer", "AI Engineer", "Artificial Intelligence Engineer"]
# # keywords = ["programming"]
# job experience Level - ex:  ["Internship", "Entry level" , "Associate" , "Mid-Senior level" , "Director" , "Executive"]
experienceLevels = ["Mid-Senior level" , "Associate", "Director", "Executive", "Entry level"]
# #job posted date - ex: ["Any Time", "Past Month" , "Past Week" , "Past 24 hours"] - select only one
datePosted = ["Past Week"]
# # datePosted = ["Past 24 hours"]
# #job type - ex:  ["Full-time", "Part-time" , "Contract" , "Temporary", "Volunteer", "Intership", "Other"]
jobType = ["Full-time", "Part-time" , "Contract"]
# #remote  - ex: ["On-site" , "Remote" , "Hybrid"]
remote = ["On-site" , "Remote" , "Hybrid"]
# #salary - ex:["$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+" ] - select only one
salary = ["$30,000+"]
# #sort - ex:["Recent"] or ["Relevent"] - select only one
sort = ["Recent"]
# #Blacklist companies you dont want to apply - ex: ["Apple","Google"]
blacklist = ["Apple","Google","Microsoft","Amazon","Facebook","Meta","Netflix","IBM","Salesforce","Oracle","SAP","Intel","Cisco","Adobe","Dell","HP","Accenture","Capgemini","Tata Consultancy Services","Cognizant","Infosys","Wipro","HCL Technologies"]
# #Blaclist keywords in title - ex:["manager", ".Net"]
blackListTitles = [""]
# #Only Apply these companies -  ex: ["Apple","Google"] -  leave empty for all companies 
onlyApply = [""]
# #Only Apply titles having these keywords -  ex:["web", "remote"] - leave empty for all companies 
onlyApplyTitles = [""] 
# #Follow companies after sucessfull application True - yes, False - no
followCompanies = False
# # your country code for the phone number - ex: fr
country_code = "IN"
# # Your phone number without identifier - ex: 123456789
phone_number = "7982473942"


# # These settings are for running AngelCO job apply bot
# AngelCoBotPassword = ""
# # AngelCO credits
# AngelCoEmail = ""
# AngelCoPassword = ""
# # jobTitle ex: ["Frontend Engineer", "Marketing"]
# angelCoJobTitle = ["Frontend Engineer"]
# # location ex: ["Poland"]
# angelCoLocation = ["Poland"]

# # These settings are for running GlobalLogic job apply bot
# GlobalLogicBotPassword = ""
# # AngelCO credits
# GlobalLogicEmail = ""
# GlobalLogicPassword = ""
# # Functions ex: ["Administration", "Business Development", "Business Solutions", "Content Engineering", 	
# # Delivery Enablement", Engineering, Finance, IT Infrastructure, Legal, Marketing, People Development,
# # Process Management, Product Support, Quality Assurance,Sales, Sales Enablement,Technology, Usability and Design]
# GlobalLogicFunctions = ["Engineering"]
# # Global logic experience: ["0-1 years", "1-3 years", "3-5 years", "5-10 years", "10-15 years","15+ years"]
# GlobalLogicExperience = ["0-1 years", "1-3 years"]
# # Global logic location filter: ["Argentina", "Chile", "Crotia", "Germany", "India","Japan", "Poland"
# # Romania, Sweden, Switzerland,Ukraine, United States]
# GlobalLogicLocation = ["poland"]
# # Freelance yes or no
# GlobalLogicFreelance = ["no"]
# # Remote work yes or no
# GlobalLogicRemoteWork = ["yes"]
# # Optional! Keyword:["javascript", "react", "angular", ""]
# GlobalLogicKeyword = ["react"]
# # Global Logic Job apply settinngs
# FirstName = "O"
# LastName = "D"
# Email = "amin@boulouma.com"
# LinkedInProfileURL = "www.google.com"
# Phone = "" #OPTIONAL
# Location = "" #OPTIONAL
# HowDidYouHeard = "" #OPTIONAL
# ConsiderMeForFutureOffers = True #true = yes, false = no

# General bot settings
browser = ["chrome"]  # or ["firefox"]
email = "amanhuriya2@gmail.com"
password = ""

# Optional! run browser in headless mode, no browser screen will be shown it will work in background.
headless = False
# Optional! for Firefox enter profile dir to run the bot without logging in your account each time
firefoxProfileRootDir = r""

# Smart AI Responder Settings (for form validation errors)
notice_period = "20"
visa_status = "Indian Citizen"
willing_to_relocate = True
followCompanies = False
cv_path = "/Users/amankumar/Desktop/Aman Kumar Huriya CV .pdf"  # If CV has different name/location
current_salary = "18"  # LPA or yearly salary
salary_expectation = "27"  # Expected salary
experience_years = "4"  # Years of experience override

# Personal details (used as fallbacks if not found in CV)
full_name = "Aman Kumar Huriya"
phone = "+91-7982473942"
current_title = "Senior Software Engineer"
education = "Bachelor in Computer Science"