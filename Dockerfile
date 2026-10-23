# syntax=docker/dockerfile:1
#
# Packages GréasánFocal Oscailte na Gaeilge with a prebuilt EWE web server (read-only, no `edit`
# feature). EWE is compiled outside the image so the image only carries the artifacts:
#
#   (cd ../ewe/ewe_dioxus && dx bundle --platform web --release)
#   docker build --build-context ewe=../ewe/target/dx/ewe/release/web -t gfong .
#   docker run -d --name gfong -p 8080:8080 --restart unless-stopped gfong
#
# Release files for the Downloads page are not in git; add `-v /path/to/downloads:/app/downloads:ro`.
# The databases are built from src/yaml and corpus/ on the first request, so the first page load
# after a fresh start is slow. To keep them across container re-creations, add
# `-v gfong-db:/app/db` and set database/corpus_database to "db/..." in settings.toml.

FROM debian:bookworm-slim
RUN useradd --system --create-home --home-dir /app ewe
WORKDIR /app
# `server` serves the client bundle from the `public` directory beside the executable.
COPY --from=ewe server ./server
COPY --from=ewe public ./public
COPY settings.toml downloads.toml logo.svg ./
COPY src/yaml src/yaml
COPY corpus corpus
RUN mkdir db && chown -R ewe:ewe /app
USER ewe
ENV IP=0.0.0.0 PORT=8080
EXPOSE 8080
CMD ["./server"]
