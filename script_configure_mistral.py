from mistral_lib import agent_management
from mistral_lib import library_management
from shared_lib.output_logging import start_logging, stop_logging, OutputLogger
from shared_lib.config_manager import config

# Configuration
bme_agent = config.get("bme_agent")
bme_agent_library = config.get("bme_agent_library")


start_logging("agent_configuration")
logger = OutputLogger()

##################################################################
logger.log_section("Main Agent Configuration", level=1)
##################################################################

logger.log_section("Agent Identifier", level=2)
logger.log(f"- Agent: {bme_agent}")

agent_management.agent_instructions(agent_id=bme_agent, new_instructions='bme_agent_instructions.md')
agent_management.set_agent_description(agent_id=bme_agent, description="Teaching and tech support agent for the Biology Meets Engineering (BME) high school program")
logger.log("✅ Agent configured successfully")

logger.log_section("Agent Library Configuration", level=2)
library_management.remove_all_documents_from_library(library_id=bme_agent_library, confirm=False)
documents = [
    'robot_details.md',
    'programming_blocks.md',
    'faculty_and_staff.md',
    'color_vision.md',
    'sonar.md',
]
for doc in documents:
    library_management.upload_document(doc, library_id=bme_agent_library)
    logger.log(f"  📄 Uploaded: {doc}")
agent_management.unassign_all_libraries_from_agent(agent_id=bme_agent)
agent_management.assign_library_to_agent(agent_id=bme_agent, library_id=bme_agent_library)
logger.log("🎉 Library configured successfully")

stop_logging()
