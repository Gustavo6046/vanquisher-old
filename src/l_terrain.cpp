#include <cmath>

#include "l_terrain.hpp"


namespace vanquisher {

	// - TerrainChunk

	TerrainChunk::TerrainChunk(int seed, int size, double base_height) : heights(size * size), seed(seed), width(size) {
		int area = width * width;

		for (int i = 0; i < area; i++) {
			this->heights[i] = base_height;
		}
	}

	double TerrainChunk::get(int x, int y) {
		return this->heights[y * this->width + x];
	}

	double TerrainChunk::get(int index) {
		return this->heights[index];
	}

	void TerrainChunk::set(int x, int y, double value) {
		this->heights[y * this->width + x] = value;
	}

	void TerrainChunk::set(int index, double value) {
		this->heights[index] = value;
	}

	void TerrainChunk::add(int x, int y, double amount) {
		this->heights[y * this->width + x] += amount;
	}

	void TerrainChunk::add(int index, double amount) {
		this->heights[index] += amount;
	}

	template<typename... Args> 
	void TerrainChunk::generate(TerrainGenerator &generator, Args... args) {
		generator.seed(this->seed);
		generator.generate(this, args...);
	}

	// - TerrainChunkIter

	TerrainChunkIterCursor::TerrainChunkIterCursor(TerrainChunk &terrain) : terrain(terrain) {
		this->area = this->width * this->width;
		this->width = terrain.width;
		this->index = 0;
		this->x = 0;
		this->y = 0;
	}

	bool TerrainChunkIterCursor::next() {
		this->index++;

		if (this->index >= this->area) {
			return false;
		}
		
		this->x = this->index % this->width;
		this->y = this->index / this->width;

		return true;
	}

	double TerrainChunkIterCursor::get() {
		return this->terrain.get(this->index);
	}

	void TerrainChunkIterCursor::set(double value) {
		return this->terrain.set(this->index, value);
	}

	void TerrainChunkIterCursor::add(double amount) {
		return this->terrain.add(this->index, amount);
	}

	void TerrainChunkIterCursor::seek(int index) {
		this->index = index;

		if (index < 0) this->index = 0;
		if (index >= this->area) this->index = this->area - 1;

		this->x = this->index % this->width;
		this->y = this->index / this->width;
	}

	void TerrainChunkIterCursor::seek(int x, int y) {
		this->seek(y * this->width + x);
	}
	
	TerrainGenerator::TerrainGenerator() : rng() {
		set_default_parameters();
	}

	void TerrainGenerator::set_default_parameters() {}

	void TerrainGenerator::seed(long int seed) {
		this->rng.seed(seed);
	}

	void TerrainGenerator::set_parameter(std::string name, double value) {
		this->params[name] = value;
	}

	void SineTerrainGenerator::set_default_parameters() {
		// values
		double amplitude = 18, offset = 30, x_scale = 32, y_scale = 42, roughness = 0.15;

		// set them
		this->params["amplitude"] = amplitude;
		this->params["offset"] = offset;
		this->params["xscale"] = x_scale;
		this->params["yscale"] = y_scale;
		this->params["roughness"] = roughness;
	}

	void SineTerrainGenerator::generate(TerrainChunk &target) {
		// parameters

		double amplitude	= this->params["amplitude"];
		double offset		= this->params["offset"];
		double roughness	= this->params["roughness"];
		double x_scale		= this->params["xscale"];
		double y_scale		= this->params["yscale"];

		// setup
	
		double half_amplitude = amplitude / 2.0;
			
		auto cursor = target.iter();
		std::uniform_real_distribution<double> dist;

		if (roughness) {
			dist = std::uniform_real_distribution<double>(-roughness * amplitude, roughness * amplitude);
		}

		// generate

		while (cursor.next()) {
			double rough = 0.0;

			if (roughness) {
				rough += dist(this->rng);
			}

			double val = offset + rough + half_amplitude * (
				sin(cursor.x * x_scale) +
				sin(cursor.y * y_scale)
			);

			cursor.add(val);
		}
	}
}
