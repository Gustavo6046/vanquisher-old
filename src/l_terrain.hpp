/**
 * Vanquisher terrain.
 */

#ifndef H_VANQUISHER_LEVEL_TERRAIN
#define H_VANQUISHER_LEVEL_TERRAIN


#include <vector>
#include <random>
#include <map>
#include <string>


namespace vanquisher {
	class TerrainChunkIterCursor;
	class TerrainGenerator;

	class TerrainChunk {
	private:
		std::vector<double> heights; 
		int seed;

	public:
		int width;

		TerrainChunk(int seed, int width, double base_height = 0.0);
		double get(int x, int y);
		double get(int index);
		void set(int x, int y, double value);
		void set(int index, double value);
		void add(int x, int y, double amount);
		void add(int index, double amount);
		TerrainChunkIterCursor iter();

		template<typename... Args> 
		void generate(TerrainGenerator &generator, Args...args);
	};

	class TerrainChunkIterCursor {
	private:
		TerrainChunk &terrain;
		int width, area;

	public:
		int index, x, y;

		TerrainChunkIterCursor(TerrainChunk &terrain);
		TerrainChunk &get_terrain();
		double get();
		void set(double value);
		void add(double amount);
		bool next();
		void seek(int x, int y);
		void seek(int index);
	};

	class TerrainGenerator {
	protected:
		std::mt19937 rng;
		std::map<std::string, double> params;
		virtual void set_default_parameters();

	public:	
		TerrainGenerator();
		void seed(long int seed);
		void set_parameter(std::string name, double value);
		virtual void generate(TerrainChunk &target) = 0;
	};

	class SineTerrainGenerator : TerrainGenerator {
	public:
		void generate(TerrainChunk &target) override;
		void set_default_parameters() override;
	};
};


#endif
