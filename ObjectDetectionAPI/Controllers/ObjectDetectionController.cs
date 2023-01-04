using Microsoft.AspNetCore.Mvc;
using NetTopologySuite.Geometries;
using Object_Detection.Data;
using System.Security.Cryptography;
using System.Net;
using MimeKit;
using System.ComponentModel.DataAnnotations;
using MimeKit.Text;
using MailKit.Net.Smtp;
using MailKit.Security;

// For more information on enabling Web API for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace Object_Detection.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class ObjectDetectionController : ControllerBase
    {
        public DataContext DataContext { get; }

        public ObjectDetectionController(DataContext DataContext) 
        { 
            this.DataContext = DataContext; 
        }

        // GET: api/<ObjectDetectionController>
        [HttpGet]
        public Response GetAllRecords()
        {
            Response Response = new Response();
            Response.Value = (from ObjectDetection in DataContext.ObjectDetections
                              select new
                              {
                                  Id = ObjectDetection.Id,
                                  ObjectName = ObjectDetection.ObjectName,
                                  Description = ObjectDetection.Description,
                                  Type = ObjectDetection.Type,
                                  Date = ObjectDetection.Date,
                              }).ToList();
            if (Response.Value == null)
            {
                Response.Status = false;
                Response.Result = "Nesne Kaydı bulunamadı";
                return Response;
            }
            Response.Status = true;
            Response.Result = "Islem basarılı";

            return Response;
        }

        // GET api/<ObjectDetectionController>/5
        [HttpGet("GetObjectRecord")]
        public Response GetObjectRecord(int Id)
        {
            Response Response = new Response();
            Response.Value = (from ObjectDetection in DataContext.ObjectDetections.Where(
                ObjectDetection => ObjectDetection.Id == Id)
                              select new
                              {
                                  Id = ObjectDetection.Id,
                                  ObjectName = ObjectDetection.ObjectName,
                                  Description = ObjectDetection.Description,
                                  Type = ObjectDetection.Type,
                                  Date = ObjectDetection.Date,
                              }).SingleOrDefault();
            if (Response.Value == null)
            {
                Response.Status = false;
                Response.Result = "Aranan Nesne Kaydı bulunamadı";
                return Response;
            }
            Response.Status = true;
            Response.Result = "Islem basarılı";

            return Response;
        }

        // POST api/<ObjectDetectionController>
        [HttpPost]
        public Response Post(ObjectDetection ObjectDetection)
        {
            Response Response = new Response();

            ObjectDetection TempObjectDetection = new ObjectDetection();

            if (ObjectDetection.ObjectName != null && ObjectDetection.Type != null
                && ObjectDetection.Date != null)
            {

                ObjectDetection objectDetection = new ObjectDetection();
                objectDetection.Id = ObjectDetection.Id;
                objectDetection.ObjectName = ObjectDetection.ObjectName;
                objectDetection.Type = ObjectDetection.Type;
                objectDetection.Date = ObjectDetection.Date;
                objectDetection.Description = ObjectDetection.Description;
                DataContext.ObjectDetections.Add(objectDetection);
                DataContext.SaveChanges();
                Response.Value = ObjectDetection;

                var email = new MimeMessage();
                email.From.Add(MailboxAddress.Parse("emrebitirmeproje@gmail.com"));
                email.To.Add(MailboxAddress.Parse("elmaciemre2@gmail.com"));
                email.Subject = "test email subject";
                email.Body = new TextPart(TextFormat.Text) { Text = ObjectDetection.ObjectName+
                    " adlı "+ObjectDetection.Type+ " objesi "+ObjectDetection.Date + " tarihinde " +
                    ObjectDetection.Description + " dersliğinde tanımlandı" };

                using var smtp = new SmtpClient();

                smtp.Connect("smtp.gmail.com", 587, SecureSocketOptions.StartTls);
                smtp.Authenticate("emrebitirmeproje@gmail.com", "jnbwwybtancyjkzf");//şifre
                smtp.Send(email);
                smtp.Disconnect(true);

                    Response.Result = "Ekleme başarılı";
                    Response.Status = false;
                    return Response;
            }
            Response.Status = false;
            Response.Result = "Boş değer giremezsiniz";
            return Response;

        }

        // PUT api/<ObjectDetectionController>/5
        [HttpPut]
        public Response UpdateRecords(ObjectDetection ObjectDetection)
        {
            Response Response = new Response();
            var TempRecord = (from _TempRecords in DataContext.ObjectDetections.Where(
                _TempRecords => _TempRecords.Id == ObjectDetection.Id)
                                select _TempRecords).SingleOrDefault();
            if (TempRecord == null)
            {
                Response.Status = false;
                Response.Result = "Aranan Kayıt bulunamadı";
                return Response;
            }
            if (ObjectDetection.Id != 0) TempRecord.Id = ObjectDetection.Id;
            if (ObjectDetection.ObjectName != null) TempRecord.ObjectName = ObjectDetection.ObjectName;
            if (ObjectDetection.Type != null) TempRecord.Type = ObjectDetection.Type;
            if (ObjectDetection.Description != null) TempRecord.Description = ObjectDetection.Description;
            if (ObjectDetection.Date != null) TempRecord.Date = ObjectDetection.Date;

            DataContext.SaveChanges();
            Response.Value = TempRecord;
            Response.Result = "Guncelleme basarili";
            Response.Status = true;
            return Response;
        }

        // DELETE api/<ObjectDetectionController>/5
        [HttpDelete]
        public Response Delete(int Id)
        {
            Response Response = new Response();
            Response.Value = (from TempRecord in DataContext.ObjectDetections.Where(
                TempRecord => TempRecord.Id == Id)
                              select TempRecord).SingleOrDefault();
            if (Response.Value == null)
            {
                Response.Status = false;
                Response.Result = "Aranan Kayıt Bulunamadı";
                return Response;
            }

            DataContext.ObjectDetections.Remove((ObjectDetection)Response.Value);
            DataContext.SaveChanges();
            Response.Status = true;
            Response.Result = "Silme İşlemi basarılı";
            return Response;
        }
    }
}
