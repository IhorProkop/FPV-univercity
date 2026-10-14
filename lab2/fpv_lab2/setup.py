from setuptools import find_packages, setup

package_name = "fpv_lab2"

setup(
    name=package_name,
    version="0.1.0",
    # find_packages, а не [package_name]: інакше підпакети
    # flight_test/handlers і target_flight/handlers не потраплять у збірку
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Ihor Prokop",
    maintainer_email="svatoslavprokop@gmail.com",
    description="Lab 2: ArduPilot SITL + Gazebo flight to a target point",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "flight_test = fpv_lab2.flight_test.main:main",
            "fly_to_target = fpv_lab2.target_flight.main:main",
        ],
    },
)
