FROM ghcr.io/valhalla/valhalla:3.9.0 AS builder
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
      cmake make g++ pkgconf git ca-certificates libboost-dev libcurl4-openssl-dev libczmq-dev \
      libzmq3-dev libluajit-5.1-dev liblz4-dev libprotobuf-dev protobuf-compiler libspatialite-dev \
      libsqlite3-dev zlib1g-dev libgeos-dev libgeos++-dev libssl-dev
RUN git clone -q --depth 1 --branch 3.9.0 --recurse-submodules --shallow-submodules \
      https://github.com/valhalla/valhalla.git /src/valhalla
COPY multimodal-exclusions.patch stop-accessibility.patch /tmp/
RUN cd /src/valhalla && git apply /tmp/multimodal-exclusions.patch /tmp/stop-accessibility.patch
ARG CONCURRENCY=4
# ENABLE_SERVICES must stay ON: without it valhalla_service is built without the HTTP server.
# ENABLE_DATA_TOOLS is needed for valhalla_convert_transit (pulls in libssl-dev).
# ENABLE_GEOTIFF=OFF only drops GeoTIFF output of isochrones (not used by us).
RUN cmake -S /src/valhalla -B /build -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc \
      -DENABLE_TESTS=OFF -DENABLE_DATA_TOOLS=ON -DENABLE_PYTHON_BINDINGS=OFF -DENABLE_SERVICES=ON \
      -DENABLE_CCACHE=OFF -DENABLE_SINGLE_FILES_WERROR=OFF -DENABLE_GEOTIFF=OFF && \
    cmake --build /build --target valhalla_service valhalla_convert_transit valhalla_build_tiles -j${CONCURRENCY} && \
    strip /build/valhalla_service /build/valhalla_convert_transit /build/valhalla_build_tiles

FROM ghcr.io/valhalla/valhalla:3.9.0
COPY --from=builder /build/valhalla_service /build/valhalla_convert_transit /build/valhalla_build_tiles /usr/local/bin/
LABEL org.opencontainers.image.description="Valhalla 3.9.0 + multimodal exclusions + stop accessibility patches"
