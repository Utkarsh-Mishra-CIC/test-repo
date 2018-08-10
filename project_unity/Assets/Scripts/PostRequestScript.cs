using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;


using System.IO;
using System.IO.IsolatedStorage;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

public class PostRequestScript : MonoBehaviour {

    string url = "https://localhost:5000/login";
    string homeUrl = "https://localhost:5000";
    //public Text username;
    //public Text password;
    //public Text renderedtext;

    public void Start()
    {
        ServicePointManager.ServerCertificateValidationCallback = TrustCertificate;

        StartCoroutine(postRequest());
    }

    IEnumerator postRequest()
    {



        string cookie = null;
        {
            WWWForm form = new WWWForm();
            form.AddField("username", "A");
            form.AddField("password", "1234");



            Debug.Log("Sending Login request");



            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                yield return www.SendWebRequest();
                if (www.isNetworkError || www.isHttpError)
                {
                    //renderedtext.text = www.error;
                }
                else
                {
                    //Debug.Log(www.downloadHandler.text);
                    //renderedtext.text = www.downloadHandler.text;

                    //foreach (var v in www.GetResponseHeaders())
                    //    Debug.Log(v.Key + ":" + v.Value);

                    if (www.GetResponseHeaders().ContainsKey("Set-Cookie"))
                        cookie = www.GetResponseHeaders()["Set-Cookie"];

                }


            }

        }

        yield return new WaitForSeconds(5);

        if (cookie != null)
        {

            //cookie = cookie.Substring(0, cookie.IndexOf(';'));

            WWWForm form = new WWWForm();
            //form.headers.Add("Cookie", cookie);

            Debug.Log("Sending Login with Cookie request cookie="+cookie);

            using (UnityWebRequest www = UnityWebRequest.Post(homeUrl, form))
            {
                www.SetRequestHeader("Cookie", cookie);

                yield return www.SendWebRequest();
                if (www.isNetworkError || www.isHttpError)
                {
                    //renderedtext.text = www.error;
                }
                else
                {
                    Debug.Log(www.downloadHandler.text);
                    //renderedtext.text = www.downloadHandler.text;

                    //foreach (var v in www.GetResponseHeaders())
                    //    Debug.Log(v.Key + ":" + v.Value);
                }
            }
        }

    }

    private static bool TrustCertificate(object sender, X509Certificate x509Certificate, X509Chain x509Chain, SslPolicyErrors sslPolicyErrors)
    {
        // all Certificates are accepted
        return true;
    }
}
