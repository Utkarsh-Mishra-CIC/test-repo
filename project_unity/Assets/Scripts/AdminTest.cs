using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;

using System.IO;
using System.IO.IsolatedStorage;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

public class AdminTest : MonoBehaviour {

    public InputField Password;
    string url = "https://localhost:5000/admin";
    public GameObject canvasObj;

    public void Admin()
    {
        ServicePointManager.ServerCertificateValidationCallback = TrustCertificate;
        StartCoroutine(postRequest());
    }

    IEnumerator postRequest()
    {
        string cookie = null;
        {
            WWWForm form = new WWWForm();
            form.AddField("password", Password.text);
            Debug.Log("Sending Login request");
            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                yield return www.SendWebRequest();
                if (!(www.isNetworkError || www.isHttpError))
                {
                    if (www.GetResponseHeaders().ContainsKey("Set-Cookie"))
                        cookie = www.GetResponseHeaders()["Set-Cookie"];
                    if (www.downloadHandler.text.Contains("Admin Portal"))
                    {
                        SceneManager.LoadScene("Demo2");
                    }
                    else
                    {
                        // signIn_FailureScreen.SetActive(true);
                    }
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
