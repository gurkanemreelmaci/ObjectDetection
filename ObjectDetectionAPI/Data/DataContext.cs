using Microsoft.EntityFrameworkCore;

namespace Object_Detection.Data
{
    public class DataContext : DbContext
    {
        public DataContext(DbContextOptions<DataContext> options) : base(options) { }

        public DbSet<ObjectDetection> ObjectDetections { get; set; }
    }
}
