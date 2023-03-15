import pynecone as pc

config = pc.Config(
    app_name="fire_detector",
    db_url="sqlite:///pynecone.db",
    env=pc.Env.DEV,
    frontend_packages=[
        "react-circular-progressbar",
    ],
)
