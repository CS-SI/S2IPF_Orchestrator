from setuptools import setup

LICENSE = open("LICENSE").read()

setup(
    name='S2IPF_Orchestrator',
    version='03.00.00',
    packages=['orchestrator'],
    url='www.csgroup.eu',
    license='ApacheV2',
    author='CS:Esquis Benjamin',
    long_description=LICENSE,
    author_email='',
    description='S2IPF service Orchestrator',
    entry_points={"console_scripts": ["orchestrator = orchestrator.orchestration:main",
                                      "servorch = orchestrator.OrchestratorService:main",
                                      "orchestratorHMI = orchestrator.orchestratorHMI:main"]}
)
