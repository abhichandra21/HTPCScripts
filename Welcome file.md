<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome file</title>
  <link rel="stylesheet" href="https://stackedit.io/style.css" />
</head>

<body class="stackedit">
  <div class="stackedit__html"><ul>
<li><strong>See all java processes running (any platform/OS version) with all parameters:</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">/usr/java/bin/jps -v
</code></pre>
<p><em>e.g. If you need to check if OutOfMemory Monitoring is setup?</em></p>
<pre class=" language-bash"><code class="prism  language-bash">/usr/java/bin/jps -v <span class="token operator">|</span> <span class="token function">grep</span> HeapDumpOnOutOfMemoryError
</code></pre>
<p><em>Sample Output:</em></p>
<pre class=" language-java"><code class="prism  language-java"><span class="token number">9382</span> ContextServer <span class="token operator">-</span>DAK<span class="token operator">=</span>PROPSERV <span class="token operator">-</span>Xms64m <span class="token operator">-</span>Xmx1024m <span class="token operator">-</span>XX<span class="token operator">:</span>MetaspaceSize<span class="token operator">=</span>128m <span class="token operator">-</span>XX<span class="token operator">:</span>MaxMetaspaceSize<span class="token operator">=</span>512m 
<span class="token operator">-</span>XX<span class="token operator">:</span>NativeMemoryTracking<span class="token operator">=</span>detail <span class="token operator">-</span>XX<span class="token operator">:</span><span class="token operator">+</span>HeapDumpOnOutOfMemoryError 
<span class="token operator">-</span>XX<span class="token operator">:</span>OnOutOfMemoryError<span class="token operator">=</span><span class="token operator">/</span>opt<span class="token operator">/</span>emageon<span class="token operator">/</span>var<span class="token operator">/</span>OutOfMemoryMonitoring<span class="token operator">/</span>heap<span class="token punctuation">.</span>sh <span class="token operator">%</span>p 
<span class="token operator">-</span>Dimageon<span class="token punctuation">.</span>jndi<span class="token punctuation">.</span>propertiescontext<span class="token punctuation">.</span>cleanupInterval<span class="token operator">=</span><span class="token number">120000</span> <span class="token operator">-</span>Djava<span class="token punctuation">.</span>rmi<span class="token punctuation">.</span>server<span class="token punctuation">.</span>hostname<span class="token operator">=</span>EMIMERCY<span class="token operator">-</span>hasvc<span class="token punctuation">.</span>allina<span class="token punctuation">.</span>com 
<span class="token operator">-</span>Dimageon<span class="token punctuation">.</span>rmi<span class="token punctuation">.</span>server<span class="token punctuation">.</span>port<span class="token operator">=</span><span class="token number">15000</span> <span class="token operator">-</span>Dimageon<span class="token punctuation">.</span>crypto<span class="token punctuation">.</span>encryptionEnabled<span class="token operator">=</span><span class="token boolean">false</span> <span class="token operator">-</span>Djava<span class="token punctuation">.</span>io<span class="token punctuation">.</span>tmpdir<span class="token operator">=</span><span class="token operator">/</span>opt<span class="token operator">/</span>emageon<span class="token operator">/</span>temp<span class="token operator">/</span>propserver 
<span class="token operator">-</span>Djava<span class="token punctuation">.</span>naming<span class="token punctuation">.</span>factory<span class="token punctuation">.</span>initial<span class="token operator">=</span>imageon<span class="token punctuation">.</span>jndi<span class="token punctuation">.</span>propertiescontext<span class="token punctuation">.</span>PropertiesContextFactory 
<span class="token operator">-</span>Djava<span class="token punctuation">.</span>naming<span class="token punctuation">.</span>provider<span class="token punctuation">.</span>url<span class="token operator">=</span>properties<span class="token operator">:</span><span class="token operator">/</span><span class="token comment">//opt/emageon/manager/etc/emageon.properties</span>
</code></pre>
<ul>
<li><strong>Check RAM configuration:</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">    1. dmidecode -t 17 <span class="token operator">|</span> <span class="token function">awk</span> <span class="token string">'begin{sum=0}/Size:.*GB$/{sum+=}END{print sum}'</span>
    2. <span class="token function">free</span> -gt
</code></pre>
<ul>
<li><strong>How many modules of what size:</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">dmidecode -t 17 <span class="token operator">|</span> <span class="token function">awk</span> <span class="token string">'/Size:.*GB$/{print}'</span>`
</code></pre>
<ul>
<li>
<p><strong>CPU info:</strong></p>
<ul>
<li>General info: <code>lscpu | grep -E '^Thread|^Core|^Socket|^CPU\('</code></li>
<li>How may cores?: <code>echo Cores = $(( $(lscpu | awk '/^Socket/{ print }') * $(lscpu | awk '/^Core/{ print }') ))</code></li>
</ul>
</li>
<li>
<p><strong>Check if the server is running SLES12:</strong></p>
</li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">pidof systemd  _<span class="token comment"># should return 1 if SLES12_</span>
</code></pre>
<ul>
<li><strong>Check the home directory of a process. Useful to look where a process creates heap dumps, crash logs etc</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">pwdx <span class="token operator">&lt;</span>PID<span class="token operator">&gt;</span>
</code></pre>
<ul>
<li><strong>List plugins and how active they are in the logs. Is helpful to find if one or more plugins are more active than usual or in comparison to other sites/days:</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash"><span class="token function">awk</span> -F\<span class="token operator">|</span> <span class="token string">'/ARCHIVE@/{print <span class="token variable">$4</span>}'</span> 20180604<span class="token punctuation">[</span>0-1<span class="token punctuation">]</span><span class="token punctuation">[</span>0-9<span class="token punctuation">]</span>.log 2018060420.log 2018060421.log <span class="token operator">|</span> <span class="token function">sort</span> <span class="token operator">|</span> <span class="token function">uniq</span> -c
</code></pre>
<pre><code>[root@EMIMERCY@AHS003004 20180604]# 
59765133 Core
2743097 Dicom PlugIn 1
   6239 EPP
 302012 HL7   
      1 Log4jQuartz - JobRunShell.java
      1 Log4jQuartz - QuartzScheduler.java 
  49081 MWL Update
1079105 Proxy 1
6844674 Router Plugin
     99 ScheduledBatchJob
   1859 ScheduledWorkEngine
6085651 StorageManager PlugIn     
     49 DefaultHTTPServer
    172 Deletor Plugin
     35 InternalJettyHTTPServer
[root@EMIMERCY@AHS003004 20180604]#
</code></pre>
<ul>
<li><strong>Check when was the last time pattern was logged in a log file (Read from bottom to top and stop at the first match):</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">tac 2018060813.log <span class="token operator">|</span> <span class="token function">grep</span> -am1 <span class="token string">"Error Storing Object"</span>
</code></pre>
<ul>
<li><strong><code>grep</code> Lookahead and Lookback example</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash"><span class="token function">grep</span> -aoP <span class="token string">'(?s)(?&lt;=xpw\x04\x00\x00\x00\x01t\x00.)([a-zA-Z]+)(?=x)'</span> testfile
</code></pre>
<ul>
<li><strong>Devices setup as Router Destinations but with no Router Rules</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash"><span class="token keyword">for</span> aa <span class="token keyword">in</span> <span class="token punctuation">$(</span>awk -F\<span class="token operator">=</span> <span class="token string">'/RouterDestination.*[|]Destination=/{print <span class="token variable">$NF</span>}'</span> /opt/emageon/manager/etc/emageon.properties <span class="token punctuation">)</span><span class="token punctuation">;</span> <span class="token keyword">do</span>
  <span class="token function">grep</span> -q <span class="token string">"PlugIn|ROUTER|.*|ScheduledDestinations|1|DestinationAE=<span class="token variable">${aa}</span>"</span> /opt/emageon/manager/etc/emageon.properties <span class="token operator">||</span> <span class="token punctuation">{</span>
    <span class="token function">read</span> -r aet desc <span class="token operator">&lt;&lt;&lt;</span><span class="token punctuation">$(</span>grep <span class="token string">"^RemoteApplicationEntities|<span class="token variable">${aa}</span>|"</span> /opt/emageon/manager/etc/emageon.properties <span class="token operator">|</span> <span class="token function">awk</span> -F\<span class="token operator">=</span> <span class="token string">'/Description|AETitle/{print <span class="token variable">$NF</span>}'</span><span class="token punctuation">)</span>
    <span class="token keyword">echo</span> <span class="token string">"<span class="token variable">${aet}</span> : <span class="token variable">${desc}</span>"</span>
  <span class="token punctuation">}</span>
<span class="token keyword">done</span>
</code></pre>
<ul>
<li><strong>Map dm devices to lvm</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash">lvdisplay<span class="token operator">|</span><span class="token function">awk</span>  <span class="token string">'/LV Name/{n=} /Block device/{d=; sub(".*:","dm-",d); print d,n;}'</span>
</code></pre>
<ul>
<li><strong>Sum/Count/Avg/Median/Max/Min Store times</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash"><span class="token function">awk</span> <span class="token string">'
  BEGIN{sum=0;c=0}
    /Total Storage time/{
    sum+=<span class="token variable"><span class="token variable">$(</span>NF-1<span class="token variable">)</span></span>
    a[c++]=<span class="token variable"><span class="token variable">$(</span>NF-1<span class="token variable">)</span></span>
    }
  END{
    n = asort(a)
    avg=sum/c
    if((c%2)==1){
      median=a[int(c/2)]
    }else{
      median=(a[c/2]+a[c/2-1])/2
    }
    printf "Sum:\t\t%s\nCount:\t\t%s\nAverage:\t%s\nMedian:\t\t%s\nMin:\t\t%s\nMax:\t\t%s\n",sum,c,avg,median,a[1],a[c-1]
  }
'</span> 2018071715.log
</code></pre>
<ul>
<li><strong>Time stamps for events in eventqueue</strong></li>
</ul>
<pre class=" language-bash"><code class="prism  language-bash"><span class="token function">find</span> /opt/emageon/log/journal/Router/eventqueue -type f 2<span class="token operator">&gt;</span>/dev/null <span class="token operator">|</span> <span class="token function">xargs</span> <span class="token function">ls</span> -l 2<span class="token operator">&gt;</span>/dev/null<span class="token operator">|</span> <span class="token function">awk</span> <span class="token string">'{printf "%s %s\n",<span class="token variable"><span class="token variable">$(</span>NF-3<span class="token variable">)</span></span>,<span class="token variable"><span class="token variable">$(</span>NF-2<span class="token variable">)</span></span>}'</span> <span class="token operator">|</span> <span class="token function">sort</span> <span class="token operator">|</span> <span class="token function">uniq</span> -c
<span class="token function">find</span> /opt/emageon/log/journal/Router/eventqueue -type f 2<span class="token operator">&gt;</span>/dev/null <span class="token operator">|</span> <span class="token function">xargs</span> <span class="token function">ls</span> -l 2<span class="token operator">&gt;</span>/dev/null<span class="token operator">|</span> <span class="token function">awk</span> <span class="token string">'{printf "%s %s %s\n",<span class="token variable"><span class="token variable">$(</span>NF-3<span class="token variable">)</span></span>,<span class="token variable"><span class="token variable">$(</span>NF-2<span class="token variable">)</span></span>,<span class="token variable"><span class="token variable">$(</span>NF-1<span class="token variable">)</span></span>}'</span> <span class="token operator">|</span> <span class="token function">sort</span> <span class="token operator">|</span> <span class="token function">uniq</span> -c
</code></pre>
<ul>
<li><strong>iostat</strong></li>
</ul>
<pre><code>iostat -dxk /dev/sda 5
</code></pre>
<blockquote>
<p>await - The average time (in milliseconds) for I/O requests issued to the device to be served. This includes the time<br>
spent by the requests in queue and the time spent servicing them.<br>
svctime - The average service time (in milliseconds) for I/O requests that were issued to the device.<br>
avgqu-sz - The average queue length of the requests that were issued to the device.</p>
</blockquote>
</div>
</body>

</html>
