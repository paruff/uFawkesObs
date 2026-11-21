# Developing

Four commands cover the loop. Config checks run in Docker; `make doctor` also needs `yq` and `nc` on the host.

```bash
make doctor            # hooks, tools, Docker, .env and free ports, with a fix hint per failure
make up                # start the stack
make lint-config       # every config validator; no stack needed
make smoke-telemetry   # send a trace, log and metric; fail naming any signal that never arrives
```

`lint-config` proves configs parse. `smoke-telemetry` proves data actually flows Collector to Tempo, Loki and Prometheus. A change to anything under `config/` needs both.

Versions, ports and signal flow: `.agents/skills/obs-stack/SKILL.md` and `compose.yaml`.
