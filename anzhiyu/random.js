var posts=["2024/07/10/GPT-4提示工程大赛冠军/","2024/07/10/hello-world/"];function toRandomPost(){
    pjax.loadUrl('/'+posts[Math.floor(Math.random() * posts.length)]);
  };