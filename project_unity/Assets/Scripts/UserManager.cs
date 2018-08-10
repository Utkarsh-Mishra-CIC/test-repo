using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class UserManager : MonoBehaviour
{

    public static UserManager userManager;

    [System.NonSerialized]
    public string UserName = "";

    [System.NonSerialized]
    public int UserID = 0;

    [System.NonSerialized]
    public string cookie = "";
    // Use this for initialization
    void Start()
    {
        if (userManager != null)
        {
            Destroy(userManager.gameObject);
            userManager = null;
        }

        DontDestroyOnLoad(gameObject);
        userManager = this;
    }
}
